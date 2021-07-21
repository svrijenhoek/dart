import datetime

import dart.Util
import dart.metrics.start_calculations
import dart.models.Handlers
import dart.handler.mongo.connector


def main():
    # step 0: load config file
    config = dart.Util.read_full_config_file()

    print(str(datetime.datetime.now()) + "\tMetrics")
    dart.metrics.start_calculations.MetricsCalculator(config).execute()


if __name__ == "__main__":
    main()
