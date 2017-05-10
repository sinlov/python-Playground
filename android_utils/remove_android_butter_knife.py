# coding=utf-8
import optparse
import os
import sys
import logging
import logging.handlers
import datetime
import re

__author__ = 'sinlov'

reload(sys)
sys.setdefaultencoding('utf-8')

# CLASS_NAME_PATTERN = re.compile('')
BUTTER_KNIFE_PATTERN = re.compile('(ButterKnife.bind\(.*?,*\s*(.*)\);)')
BIND_PATTERN_OLD = re.compile('(@Bind\((.*?)\)\s*(.*?)\s+(.*?);)')
BIND_PATTERN_NEW = re.compile('(@BindView\((.*?)\)\s*(.*?)\s+(.*?);)')
CLICK_PATTERN = re.compile('(@OnClick\(\s*\{?(.*?)\}\s*\))')
CLASS_IMPLEMENTS_VIEW_ON_CLICK_LISTENER_PATTERN = re.compile('(.*?class.*?implements.*?View.OnClickListener.*?)')

REMOVE_BUTTER_KNIFE_IMPORT_BASE_PATTERN = re.compile('(import butterknife.ButterKnife;)')
REMOVE_BUTTER_KNIFE_IMPORT_BIND_VIEW_PATTERN = re.compile('(import butterknife.BindView;)')
REMOVE_BUTTER_KNIFE_IMPORT_ON_CLICK_PATTERN = re.compile('(import butterknife.OnClick;)')

FIND_VIEW_FORMAT_WITH_VIEW = '        %s = (%s) %sfindViewById(%s);\n'
# FIND_VIEW_FORMAT = '        %s = (%s) findViewById(%s);\n'
SET_CLICK_FORMAT = '        %s.setOnClickListener(this);\n'
SET_CLICK_FORMAT_BY_FIND_VIEW = '        %sfindViewById(%s).setOnClickListener(this);\n'

# NEW METHOD NAME OF FIND VIEW
NEW_METHOD_NAME_OF_FIND_VIEW = 'initViewByFindViewByID'

is_verbose = False
is_new_bind_version = False
is_try_to_replace_on_click = False


def verbose_print(info=str):
    logger.info(info)
    if is_verbose:
        print info


def init_log(root_dir=str):
    global logger
    log_now = datetime.datetime.now()
    log_file_format = log_now.strftime('%y%m%d%H%M%S')
    log_name = 'log_' + log_file_format + '.log'
    log_file = os.path.join(root_dir, log_name)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger = logging.getLogger('sinlov')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    print 'log init at path: %s\n' % log_file


def check_work_path(path=str):
    print '=== Now work root dir===\n=> %s\n' % path
    # os.chdir(path)
    init_log(path)


def insert_find_view_method(source=str, add=str):
    pos = source.rfind('}')
    changed = source[:pos] + add
    if pos + 1 < len(source):  # not last
        changed += source[pos + 1:]
    return changed


def get_click_str(binds, click_id, view):
    for i in binds:
        if click_id == i[1].replace(' ', ''):
            return str.format(SET_CLICK_FORMAT % (i[3]))
    return str.format(SET_CLICK_FORMAT_BY_FIND_VIEW % (view, click_id))


def replace_butter_knife(java_path):
    with open(java_path) as java_file:
        content = java_file.read()

        find_butter_class = BUTTER_KNIFE_PATTERN.findall(content)
        m_view = ""

        if find_butter_class:
            start_butt_file_replace = '=> Find butter knife java class Name %s' % os.path.split(java_path)[1]
            print start_butt_file_replace
            logger.info(start_butt_file_replace)
            verbose_print('butter knife java res path: %s' % java_path)
            butter = find_butter_class[0]

            # remove import of bind view
            content = remove_import_of_butter_knife(content, REMOVE_BUTTER_KNIFE_IMPORT_BASE_PATTERN)
            content = remove_import_of_butter_knife(content, REMOVE_BUTTER_KNIFE_IMPORT_BIND_VIEW_PATTERN)

            content = content.replace(butter[0], "%s();" % NEW_METHOD_NAME_OF_FIND_VIEW)
            if butter[0].find(',') != -1 and butter[1]:
                m_view = butter[1].split(',')[1].replace(" ", "") + '.'

            if is_new_bind_version:
                binds = BIND_PATTERN_NEW.findall(content)
            else:
                binds = BIND_PATTERN_OLD.findall(content)
            init_method = '\n    private void %s() {\n' % NEW_METHOD_NAME_OF_FIND_VIEW
            for bind in binds:
                view_id = bind[1]
                view_type = bind[2]
                view_filed = bind[3]
                verbose_print('Find butter knife bind view_id %s , view_type %s , view_filed %s' % (
                    view_id, view_type, view_filed))
                content = content.replace(bind[0], 'private' + " " + view_type + " " + view_filed + ";")
                # if m_view:
                init_method += str.format(FIND_VIEW_FORMAT_WITH_VIEW % (view_filed, view_type, m_view, view_id))
                # else:
                #     init_method += str.format(FIND_VIEW_FORMAT % (view_filed, view_type, view_id))

            if is_try_to_replace_on_click:
                # if want change replace OnClick review this
                onclick = CLICK_PATTERN.findall(content)
                if onclick:
                    content = remove_import_of_butter_knife(content, REMOVE_BUTTER_KNIFE_IMPORT_ON_CLICK_PATTERN)
                    warning_on_click_inject = '\t-> Fix Warning OnClick Inject need fix \nPath: %s\n' % java_path
                    print warning_on_click_inject
                    logger.warn(warning_on_click_inject)
                    content = content.replace(onclick[0][0], '@Override')
                    click_ids = onclick[0][1].replace(' ', '').split(',')
                    for click_id in click_ids:
                        # print click_id
                        init_method += get_click_str(binds, click_id, m_view)

            init_method += "    }\n}"

            content = insert_find_view_method(content, init_method)
            java_file.close()
            new = open(java_path, "wb")
            new.write(content)
            new.close()

            class_implements_warning = CLASS_IMPLEMENTS_VIEW_ON_CLICK_LISTENER_PATTERN.findall(content)
            if class_implements_warning:
                warning_fix_method_of_class = '\t-> Fix Warning class has implements View.onClick at\nPath: %s\n' % java_path
                print warning_fix_method_of_class
                logger.warn(warning_fix_method_of_class)

            print_done_info = '=> Done Java file path: %s' % java_path
            print print_done_info
            logger.info(print_done_info)


def remove_import_of_butter_knife(content, pattern):
    import_base = pattern.findall(content)
    if import_base:
        for import_b in import_base:
            content = content.replace(import_b, '')
    return content


def find_out_java_res(root_path=str):
    try:
        for root, dirs, files in os.walk(root_path):
            for f in files:
                if os.path.splitext(f)[1] == '.java':
                    res_java_path = os.path.join(root, f)
                    # print 'find out java at path %s' % res_java_path
                    replace_butter_knife(res_java_path)
    except Exception, ex:
        logger.error('error use not input %s' % str(ex))
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "You must input params or see -h"
        exit(1)
    check_p = str(sys.argv[1])
    if not check_p.startswith('-'):
        print 'You params is error please see -h'
        exit(1)
    parser = optparse.OptionParser('Butter Knife Inject Remove utils\npython %prog ' + '-r [projectRootPath]')
    parser.add_option('-v', '--verbose', dest='v_verbose', action="store_true", help="see verbose", default=False)
    parser.add_option('-r', '--rootPath', dest='rootPath', type="string",
                      help="android studio project root path Default is pwd or '' ",
                      metavar="pwd", default="pwd")
    parser.add_option('-m', '--methodNewBindView', dest='methodNewBindView', type="string",
                      help="new bind view method name Default is initViewByFindViewByID",
                      metavar="initViewByFindViewByID")
    parser.add_option('-n', '--newButterKnifeVersion', dest='newButterKnifeVersion', action="store_true",
                      help="choose version of default is @Bind if use is @BindView",
                      default=False)
    parser.add_option('-c', '--onClickReplace', dest='onClickReplace', action="store_true", help="see verbose",
                      default=False)
    (options, args) = parser.parse_args()
    if options.v_verbose:
        is_verbose = True
    if options.newButterKnifeVersion:
        is_new_bind_version = True
    if options.onClickReplace:
        is_try_to_replace_on_click = True
    input_root_path = os.getcwd()
    print input_root_path
    if options.rootPath is not None:
        if options.rootPath is not 'pwd' and options.rootPath is not '':
            input_root_path = options.rootPath
            exists = os.path.exists(input_root_path)
            if not exists:
                print 'You input path is not exists!'
                exit(1)
    if options.methodNewBindView is not None:
        print 'new bind view method name is: %s' % options.methodNewBindView
        NEW_METHOD_NAME_OF_FIND_VIEW = options.methodNewBindView
    check_work_path(input_root_path)
    try:
        input_is_start_remove = raw_input(r'Please press yes to start replace butter knife, other is exit: ')
        if input_is_start_remove == 'yes':
            print '=== start replace ==='
            logger.info('=== start replace ===')
            find_out_java_res(input_root_path)
            print '=== end replace ==='
            logger.info('=== end replace ===')
        else:
            print 'stop android butter knife replace, exit 0'
    except KeyboardInterrupt, e:
        logger.error('error use not input %s', str(e))
        pass
