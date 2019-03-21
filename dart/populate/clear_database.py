import sys
import getopt
from dart.handler.elastic.connector import Connector

# this script van be executed to clear all generated data. Use parameters in the following way:
# --documents Y/N --users Y/N --popularity Y/N --recommendations Y/N
# note that when documents are deleted, the popularity will automatically also be deleted.


def main(argv):
    try:
        opts, arg = getopt.getopt(argv, "hd:u:p:r:t:", ["documents=", "users=", "popularity=", "recommendations=", "termvectors="])
    except getopt.GetoptError:
        print('clear_database.py -d <Y/N> -u <Y/N> -p <Y/N -r <Y/N>')
        sys.exit(2)
    connector = Connector()
    for opt, _ in opts:
        if opt == '-h':
            print('clear_database.py -d <Y/N> -u <Y/N> -p <Y/N -r <Y/N>')
            sys.exit()
        # Delete documents
        elif opt in ("-d", "--documents"):
            if arg == "Y":
                print("Documents deleted")
                connector.clear_index('articles')
            elif arg == "N":
                print("Documents not deleted")
            else:
                print("Command unknown, documents not deleted")
        # Delete users
        elif opt in ("-u", "--users"):
            if arg == "Y":
                print("Users deleted")
                connector.clear_index('users')
            elif arg == "N":
                print("Users not deleted")
            else:
                print("Command unknown, users not deleted")
        # Delete popularity
        elif opt in ("-p", "--popularity"):
            if arg == "Y":
                print("Popularity deleted")
                # connector.clear_index('popularity')
            elif arg == "N":
                print("Popularity not deleted")
            else:
                print("Command unknown, popularity not deleted")
        # Delete recommendations
        elif opt in ("-r", "--recommendations"):
            if arg == "Y":
                print("Recommendations deleted")
                connector.clear_index('recommendations')
            elif arg == "N":
                print("Recommendations not deleted")
            else:
                print("Command unknown, recommendations not deleted")
        # Delete recommendations
        elif opt in ("-t", "--termvectors"):
            if arg == "Y":
                print("Term vectors deleted")
                connector.clear_index('termvectors')
            elif arg == "N":
                print("Term vectors not deleted")
            else:
                print("Command unknown, term vectors not deleted")


if __name__ == "__main__":
    main(sys.argv[1:])
