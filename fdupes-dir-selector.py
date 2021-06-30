import sys
from os import path
from argparse import ArgumentParser

def is_parent_dir(from_dir, to_dir):
    """
    Check if from_dir is a parent of to_dir.

    >>> is_parent_dir('./dir-a', './dir-a')
    True
    >>> is_parent_dir('./dir-a', './dir-b')
    False
    >>> is_parent_dir('./dir-a', './dir-a/subdir')
    False
    >>> is_parent_dir('./dir-a/subdir', './dir-a')
    True
    """
    diff = path.relpath(to_dir, from_dir)

    if diff == '.': return True

    for segment in diff.split('/'):
        if segment != '..': return False

    return True

def file_belongs_to_a_directory(file, directories):
    """
    Check if file is a child of any of the given directories.

    >>> file_belongs_to_a_directory('./dir-a/file', ('./dir-a',))
    True
    >>> file_belongs_to_a_directory('./dir-a/file', ('./dir-b',))
    False
    >>> file_belongs_to_a_directory('./dir-a/file', ('./dir-a/subdir',))
    False
    >>> file_belongs_to_a_directory('./dir-c/subdir/file', ('./dir-a','./dir-c'))
    True
    """
    file_dir = path.dirname(file)
    for directory in directories:
        if is_parent_dir(file_dir, directory): return True

    return False

def handle_group(group, dirs):
    if len(group) < 2:
        raise Exception('Found group with less than 2 files')

    matched_files = []
    non_matched_files = []

    for file in group:
        if file_belongs_to_a_directory(file, dirs):
            matched_files.append(file)
        else:
            non_matched_files.append(file)

    if len(non_matched_files) == 0:
        # all files in the group matched, so deleting them would remove all
        # copies of the content. skip matching this group
        return ((), group)
    else:
        return (matched_files, non_matched_files)

def parse_fdupes_groups(input_stream):
    """
    Parse an fdupes-style input stream into groups of files. Each group of matched files
    represents files that have the same contents, according to fdupes.
    """
    current_file_group = []

    for line in input_stream.readlines():
        line = line.rstrip('\n')

        if line == None: break

        if line == '' and len(current_file_group) != 0:
            # blank lines separate file groups. the current file group is
            # finished so start a new one
            yield current_file_group
            current_file_group = []
        elif line.strip() != '':
            # the line is a file, add it to the group
            current_file_group.append(line)
        else:
            raise Exception('Found a bad line: "' + line + '"')

    # flush out last file group
    if len(current_file_group) != 0:
        yield current_file_group


def main(input_stream):
    argparser = ArgumentParser(
        description='Read a fdupes-style file group list and print out files contained in a given set of directories, that can be deleted without data loss. The fdupes-style file group list is read from STDIN, files in matching dirs that can be safely deleted are written to STDOUT, and file groups that aren\'t matched or cannot be safely deleted are written to STDERR.'
    )
    argparser.add_argument('dirs',
        metavar='DIRECTORY',
        nargs='+',
        help='The directories to select.'
    )
    args = argparser.parse_args()

    first_non_matched_file_group = True

    for group in parse_fdupes_groups(input_stream):
        (matched_files, non_matched_files) = handle_group(group, args.dirs)
        if len(matched_files) > 0:
            print('\n'.join(matched_files), file=sys.stdout)

        if len(non_matched_files) > 1:
            # all non_matched file groups after the first need to be separated
            # by blank lines
            if first_non_matched_file_group:
                first_non_matched_file_group = False
            else:
                print('', file=sys.stderr)

            print('\n'.join(non_matched_files), file=sys.stderr)


if __name__ == '__main__':
    main(sys.stdin)
