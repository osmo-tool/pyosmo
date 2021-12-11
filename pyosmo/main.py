# pylint: disable=wrong-import-position,no-value-for-parameter,deprecated-method,wrong-import-order
import inspect
import sys
from logging import getLogger
from os.path import isfile, splitext, abspath, join

import click

# Set PYTHONPATH
sys.path.append(abspath(join(__file__, '..')))

from pyosmo.algorithm import WeightedAlgorithm, RandomAlgorithm
from pyosmo.end_conditions import Length
from pyosmo import Osmo, OsmoModel

log = getLogger(__name__)
import importlib


def is_osmo_model(item) -> bool:
    return inspect.isclass(item) and issubclass(item, OsmoModel) and item.__name__ != 'OsmoModel'


@click.command()
@click.argument('models', nargs=-1, type=click.Path(exists=False))
@click.option('--algorithm', '-a', required=False, default='weighted', help="Algorithm to be used",
              type=click.Choice(['random', 'weighted']))
@click.option('--test-len', '-tl', required=False, default=None, type=int, help="Length of test steps in one test")
@click.option('--suite-len', '-sl', required=False, default=None, type=int, help="Length of test suite")
def pyosmo_cli(models, algorithm, test_len, suite_len):
    """ Commandline interface for pyosmo """
    click.echo('Adding models to the Osmo')
    osmo = Osmo()
    for model_path in models:
        if not isfile(model_path):
            raise click.ClickException(f'cannot load: {model_path} file not exits')
        click.echo(f'Loading: {model_path}')
        source = importlib.machinery.SourceFileLoader(splitext(model_path)[0], model_path)  # noqa
        imported = source.load_module()
        for _, temp_class in vars(imported).items():
            if is_osmo_model(temp_class):
                osmo.add_model(temp_class())

    if algorithm is not None:
        if algorithm == 'weighted':
            osmo.algorithm = WeightedAlgorithm()
        elif algorithm == 'random':
            osmo.algorithm = RandomAlgorithm()
        else:
            raise click.ClickException(f'{algorithm} is not one of [random,weighted]')

    if test_len:
        osmo.test_end_condition = Length(test_len)

    if suite_len:
        osmo.test_suite_end_condition = Length(suite_len)

    click.echo('Start running..')
    osmo.run()
    osmo.history.print_summary()
    click.echo('All done!')


if __name__ == '__main__':
    pyosmo_cli()
