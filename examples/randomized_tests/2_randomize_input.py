import random
import time


def system_under_testing(data):
    if data < 900:
        # Flaky bug here
        return 'error'
    return data * 2


def test():
    # Send test data
    data = random.randint(1, 10000)
    output = system_under_testing(data)

    # Check that output is integer
    try:
        int(output)
    except:
        raise Exception('Data is not integer') from output

    # If we know logic of answer we can use that
    # now output should be 2 times input
    assert output == (2 * data)


if __name__ == '__main__':
    # Loop test to see how easily test can find a bug
    index = 0
    while True:
        index += 1
        print(f'Test {index}')
        time.sleep(0.1)
        test()
