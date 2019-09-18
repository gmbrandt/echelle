"""
main.py: Main driver script for the minimal pipeline included with this package.

This is inspired by the Template Method Pattern and the Framework of Banzai by Curtis McCully.

"""
import logging as logger
from ast import literal_eval
from configparser import ConfigParser

from echelle.utils.runtime_utils import parse_args, get_data_paths, order_data, select_data_of_type, load_class


class RuntimeContext(object):
    def __init__(self, dictionary):
        for attribute, value in dictionary.items():
            setattr(self, attribute, value)


def reduce_data(data_paths=None, args=None, config=None):
    if args is None:
        args = parse_args()
    if config is None:
        config = ConfigParser()
        config.read(args.config_File)
    if data_paths is None:
        data_paths = args.data_paths

    runtime_context, data_class, extension, header_keys, type_translator = organize_config(config)
    DataClass = load_class(data_class)

    for data_path in data_paths:
        logger.info('Reducing {path} assuming a data class of {data_class} and raw data in extension {extension}'
                    ''.format(path=data_path, data_class=data_class, extension=extension))

        data = DataClass.load(data_path, extension)
        frame_type = type_translator[data.header[header_keys['type']]]
        stages_todo = [load_class(stage) for stage in literal_eval(config.get('stages', frame_type))]

        for stage in stages_todo:
            data = stage(runtime_context).do_stage(data)
                # consider feeding in the logger as do_stage(data, logger)

        # data.update_filepath(base_dir=args.output_dir)
        logger.info('Writing output to {path}'.format(path=data.filepath))
        data.write(fpack=args.fpack)


def run():
    # parse command line arguments and the configuration file.
    args = parse_args()
    config = ConfigParser()
    config.read(args.config_file)

    # get the data paths of the data to reduce.
    runtime_context, data_class, extension, header_keys, type_translator = organize_config(config)
    DataClass = load_class(data_class)
    data_paths = select_data(args.input_dir, args.frame_type, literal_eval(config.get('data', 'files_contain')),
                             DataClass, extension, header_keys, type_translator)

    logger.info('Found {0} files of {1} type'.format(len(data_paths), args.frame_type))
    reduce_data(data_paths, args, config)


def organize_config(config):
    # pull information from the configuration file.
    runtime_context = RuntimeContext({key: literal_eval(item) for key, item in config.items('reduction')})
    data_class = config.get('data', 'data_class', fallback='echelle.images.Image')
    extension = config.getint('data', 'primary_data_extension')
    header_keys = literal_eval(config.get('data', 'header_keys'))
    type_translator = literal_eval(config.get('data', 'type_keys'))
    return runtime_context, data_class, extension, header_keys, type_translator


def select_data(input_dir, frame_type, files_contain, data_class, extension, header_keys, type_translator):
    data_paths = get_data_paths(input_dir, files_contain)
    data_paths = order_data(data_paths, data_class, extension, header_keys, type_translator)
    data_paths = select_data_of_type(data_paths, data_class, extension, header_keys, type_translator, frame_type)
    return data_paths

