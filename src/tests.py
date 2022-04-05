import glob
import subprocess
import sys


class Tests:
    '''Class responsible for running tests.'''

    def run_all(self, pattern: str = '**/test_*', root_dir: str = '../test') -> list[str]:
        '''Runs all tests following patter in the folder specified as root_dir. Returns the list of test files with failed tests.'''

        test_files = glob.glob(pattern, root_dir=root_dir)

        failed_test_files = []

        for test_file in test_files:
            code = subprocess.call(['python',  f'{root_dir}/{test_file}'], env={ 'PYTHONPATH': '.' })

            if code > 0:
                failed_test_files.append(test_file)

        return failed_test_files

    def run(self, test_path: str, root_dir: str = '../test') -> int:
        '''Runs the specified test file in the folder specified as root_dir. Returns the code returned by the test file.'''

        code = subprocess.call(['python',  f'{root_dir}/{test_path}'], env={ 'PYTHONPATH': '.' })

        return code


if __name__ == '__main__':
    if len(sys.argv) > 1:
        to_run = sys.argv[1]

        test_code = Tests().run(to_run)
        
        exit(test_code)

    failed_tests = Tests().run_all()

    print()
    print()

    if len(failed_tests) > 0:
        print(f'Failed test files: {failed_tests}')
        exit(1)

    print('All tests passed successfully')
    exit(0)
