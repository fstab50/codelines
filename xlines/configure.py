"""
Summary.

    Configuration Module -- configure run time parameters & exclusions

"""
import os
import sys
import inspect
import logging
from xlines.usermessage import stdout_message
from xlines.colormap import ColorMap
from xlines._version import __version__
from xlines.statics import PACKAGE
from xlines.variables import *

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

cm = ColorMap()

try:

    from xlines.oscodes_unix import exit_codes
    os_type = 'Linux'

except Exception:
    from xlines.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'


def display_exclusions(expath, exdirpath):
    """
    Show list of all file type extensions which are excluded
    from line total calculations
    """
    tab = '\t'.expandtabs(15)

    # numbering
    div = cm.bpl + ')' + rst

    try:

        if os.path.exists(expath):
            with open(expath) as f1:
                exclusions = [x.strip() for x in f1.readlines()]

        stdout_message(message='File types excluded from line totals:')

        for index, ext in enumerate(exclusions):
            print('{}{:>3}{}'.format(tab, index + 1, div + '  ' + ext))

        sys.stdout.write('\n')
        return True

    except OSError as e:
        fx = inspect.stack()[0][3]
        stdout_message(message=f'{fx}: Error: {e}. ', prefix='WARN')
        return False


def condition_map(letter, expath, exdirpath):
    return {
        'a': _configure_add,
        'b': _configure_remove,
        'c': _configure_hicount,
        'd': lambda x, y: sys.exit
    }.get(letter, lambda x, y: None)(expath, exdirpath)


def main_menupage(exclusion_files, exclusions_dirs):
    """Displays main configuration menu jump page and options"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print('''
    ________________________________________________________________________________


        ''' + bdwt + PACKAGE + rst + ''' configuration main menu:


              a)  Add file type to exclusion list

              b)  Remove file type from exclusion list

              c)  Set high line count threshold (''' + acct + 'highlight' + rst + ''' file objects)

              d)  quit

    ________________________________________________________________________________
    ''')
    loop = True
    tab8 = '\t'.expandtabs(8)

    while loop:
        answer = input('{}Choose operation [quit]: '.format(tab8)).lower()
        sys.stdout.write('\n')

        if not answer:
            return True
        elif answer in ['a', 'b', 'c', 'd']:
            condition_map(answer, expath, exdirpath)
            loop = False
        else:
            stdout_message(
                    message='You must provide a letter a, b, c, or d',
                    indent=16,
                    prefix='INFO'
                )
            sys.stdout.write('\n')


def _configure_add(expath, exdirpath):
    """
        Add exclusions and update runtime constants

    Returns:
        Success | Failure, TYPE: bool
    """
    try:

        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        display_exclusions(expath, exdirpath)

        with open(expath) as f1:
            exclusions = [x.strip() for x in f1.readlines()]

        # query user input for new exclusions
        response = input('  Enter file extension types to be excluded separated by commas [quit]: ')

        if not response:
            sys.exit(exit_codes['EX_OK']['Code'])
        else:
            add_list = response.split(',')

            # add new extensions to existing
            exclusions.extend([x if x.startswith('.') else '.' + x for x in add_list])

            # write out new exclusions config file
            with open(expath, 'w') as f2:
                f2.writelines([x + '\n' for x in exclusions])

            display_exclusions(expath, exdirpath)    # display resulting exclusions set
            return True

    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False


def _configure_rewrite(expath, newlist):
    """
        Rewrite existing exclusion list on local filesystem with
        modified contents from _configure operation

    Return:
        Succsss || Failure, TYPE: bool
    """
    try:
        # write new exclusion list to local disk
        with open(expath, 'w') as f1:
            list(filter(lambda x: f1.write(x + '\n'), newlist))

    except OSError as e:
        fx = inspect.stack()[0][3]
        stdout_message(
            f'{fx}: Problem writing new file type exclusion list: {expath}: {e}',
            prefix='WARN')
        return False
    return True


def _configure_remove(expath, exdirpath):
    """
        Remove file type extension from exclusion list

    Return:
        Succsss || Failure, TYPE: bool
    """
    tab8 = '\t'.expandtabs(8)
    loop = True

    try:
        # print out current exclusion list contents
        display_exclusions(expath, exdirpath)

        # open current file type exclusions
        with open(expath) as f1:
            f2 = [x.strip() for x in f1.readlines()]

        while loop:
            answer = input(tab8 + 'Pick a number to remove [none]: ')
            if int(answer) in range(1, len(f2) + 1) or not answer:
                loop = False
            else:
                max_index = len(f2)
                stdout_message(
                    message=f'You must pick a number between 1 and {max_index}',
                    prefix='WARN'
                )

        if not answer:
            sys.stdout.write('\n')
            return True
        else:
            # correct for f2 list index
            answer = int(answer) - 1
            # remove entry selected by user
            deprecated = f2[answer]
            f2.pop(int(answer))

        if not _configure_rewrite(expath, f2):
            return False

        # show new exclusion list contents
        display_exclusions(expath, exdirpath)    # display resulting exclusions set

        # Acknowledge removal
        if str(answer) in f2:
            stdout_message(
                message='Failure to remove {} - reason unknown'.format(f2[answer]),
                indent=16,
                prefix='FAIL')

        else:
            stdout_message(
                    message='Successfully removed file type exclusion: {}'.format(deprecated),
                    indent=16,
                    prefix='ok'
                )
    except OSError:
        stdout_message(
            message='Unable to modify local config file located at {}'.format(expath),
            prefix='WARN')
        return False


def _configure_hicount(expath, exdirpath):
    print('set hicount -- stub\n')
    pass
