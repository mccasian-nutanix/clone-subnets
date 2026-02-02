import time


class Configuration:
  def __init__(self, log, args) -> None:
    """
    @param args
      This parameter is an object which contain all the args supplied when starting the script
    @param config_file_name
      This parameter is the name of the config file, which by default is conf.yaml
    """
    self.log                            = log

    self.current_timestamp              = time.time()
    self.args                           = args