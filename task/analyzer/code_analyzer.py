# write your code here
import constants


def get_file(filepath):
    try:
        file = open(filepath)
    except IOError as err1:
        print(err1)
    else:
        return file


def check_pep_length(file):
    for i, line in enumerate(file):
        if len(line) > constants.PEP_LINE_MAX:
            print(f"Line {i+1}: {constants.LONG_LINE_CODE} Too long")


def main():
    file = get_file(input())
    check_pep_length(file)


if __name__ == '__main__':
    main()
