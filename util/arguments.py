import argparse

# APP  variables
APP_VERSION = "1.0"
APP_AUTHOR = "Casian Merce"
APP_WEBSITE = "https://mccasian.eu/"


def get_args() -> object:
    """
    This function is reading the arguments and return them as object

    Returns an object containing all the arguments used to start the script
    """

    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source-cluster',       required=True)
    parser.add_argument('-d', '--destination-cluster',  required=True)
    parser.add_argument('-v', '--source-bridge',        required=True)
    parser.add_argument('-x', '--destination-bridge',   required=True)
    parser.add_argument('-u', '--api-user',             required=True)
    parser.add_argument('-p', '--api-pass',             required=True)
    parser.add_argument('--log-level',                  required=True)


    args = parser.parse_args()

    return args