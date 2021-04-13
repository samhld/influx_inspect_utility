import inspect_util.db_util as util
import config as cfg

dbrp_path = cfg.dbrp_path
shard_names = util.load_shard_names(dbrp_path)
file_paths = util.load_file_paths(dbrp_path)

inspections = [util.inspect(file_path) for file_path in file_paths]

print(len(inspections))