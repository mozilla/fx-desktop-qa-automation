import os

from dotenv import load_dotenv

from modules import testrail_integration as tr

if __name__ == "__main__":
    # os.environ['TESTRAIL_REPORT'] = 'true'
    # os.environ['FX_L10N'] = 'true'
    load_dotenv()
    # tr.reportable('Darwin')
    case_ids = [
        2886580,
        2888568,
        2888557,
        2888561,
        2888558,
        2888556,
        2888567,
        2888559,
        2888569,
        2888562,
        2888563,
        2888560,
        2888570,
        2888571,
        2886581,
        2888701,
        2888564,
        2886598,
        2886595,
        2888565,
        2886597,
        2886599,
        2888703,
        2886601,
        2886600,
        2886602,
        2889441,
    ]
    session = tr.testrail_init()
    for i in case_ids:
        print(i)
        print(session.get_test_case(i))
