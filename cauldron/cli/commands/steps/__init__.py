import typing
from argparse import ArgumentParser

import cauldron
from cauldron import cli
from cauldron import environ
from cauldron.cli.commands.steps import actions
from cauldron.cli.interaction import autocompletion

NAME = 'steps'
DESCRIPTION = """
    Carry out an action on one or more steps within the currently opened
    project. The available actions are:
        * [add]: Creates a new step
        * [list]: Lists the steps within the currently opened project
        * [modify]: Modifies an existing step
        * [remove]: Removes an existing step from the project
    """


def populate(
        parser: ArgumentParser,
        raw_args: typing.List[str],
        assigned_args: dict
):
    """

    :param parser:
    :param raw_args:
    :param assigned_args:
    :return:
    """

    if len(raw_args) < 1:
        assigned_args['action'] = 'list'
        return

    action = raw_args.pop(0).lower()
    assigned_args['action'] = action

    if action != 'list':
        parser.add_argument(
            'step_name',
            type=str,
            help=cli.reformat(
                """
                The name of the step on which to carry out the steps action
                """
            )
        )

    if action in ['add', 'modify']:
        parser.add_argument(
            '-p', '--position',
            dest='position',
            type=str,
            default=None,
            help=cli.reformat(
                """
                Specifies the index where the step will be inserted, or the
                name of the step after which this new step will be inserted.
                """
            )
        )

        parser.add_argument(
            '-t', '--title',
            dest='title',
            type=str,
            default=None,
            help=cli.reformat(
                """
                This specifies the title for the step that will be added or
                modified
                """
            )
        )

    if action == 'modify':
        parser.add_argument(
            '-n', '--name',
            dest='new_name',
            type=str,
            default=None,
            help=cli.reformat(
                """
                This new name for the step when modifying an existing one
                """
            )
        )

    if action == 'remove':
        parser.add_argument(
            '-k', '--keep',
            dest='keep',
            default=False,
            action='store_true',
            help=cli.reformat(
                """
                Whether or not to keep the source file when removing a step
                from a project
                """
            )
        )


def execute(
        parser: ArgumentParser,
        action: str = None,
        step_name: str = None,
        position: str = None,
        title: str = None,
        new_name: str = None,
        keep: bool = False
):
    """

    :return:
    """

    if not cauldron.project or not cauldron.project.internal_project:
        environ.output.fail().notify(
            kind='ERROR',
            code='NO_OPEN_PROJECT',
            message='No project is open. Step commands require an open project'
        ).console(
            whitespace=1
        )
        return

    if not action or action == 'list':
        actions.echo_steps()
        return

    if not step_name:
        environ.output.fail().notify(
            kind='ABORTED',
            code='NO_STEP_NAME',
            message='A step name is required for this command'
        ).console(
            whitespace=1
        )
        return

    if action == 'add':
        actions.create_step(
            step_name,
            position=position,
            title=title.strip('"') if title else title
        )
        return

    if action == 'modify':
        actions.modify_step(
            name=step_name,
            new_name=new_name,
            title=title,
            position=position
        )

    if action == 'remove':
        actions.remove_step(
            name=step_name,
            keep_file=keep
        )


def autocomplete(segment: str, line: str, parts: typing.List[str]):
    """

    :param segment:
    :param line:
    :param parts:
    :return:
    """

    if len(parts) < 2:
        return autocompletion.matches(
            segment,
            parts[0],
            ['add', 'list', 'remove', 'modify']
        )

    action = parts[0]
    if action == 'list':
        return []

    project = cauldron.project.internal_project

    if len(parts) < 3:
        step_names = [x.definition.name for x in project.steps]
        return autocompletion.match_in_path_list(
            segment,
            parts[-1],
            step_names
        )

    if parts[-1].startswith('-'):
        if action == 'list':
            return []

        shorts = []
        longs = []

        if action == 'remove':
            shorts.append('k')
            longs.append('keep')
        else:
            shorts += ['p', 't']
            longs += ['position', 'title']

        if action == 'modify':
            shorts.append('n')
            longs.append('name')

        return autocompletion.match_flags(
            segment=segment,
            value=parts[-1],
            shorts=shorts,
            longs=longs
        )

    return []


