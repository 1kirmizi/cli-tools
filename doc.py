import os
import sys
from types import FunctionType
from mdutils.tools.tools import Table
from mdutils.mdutils import MdUtils
import mdutils
from pathlib import Path
import re

sys.path.append(os.path.abspath('./src'))
from codemagic import cli
from codemagic import tools

class ArgumentsSerializer:
    def __init__(self, raw_arguments):
        self.raw_arguments = raw_arguments
        self.required_args = []
        self.optional_args = []

    def serialize(self):
        for arg in self.raw_arguments:
            argument = {
                'key': arg._value_.key,
                'description': str_plain(arg._value_.description),
                'flags': ', '.join(getattr(arg._value_, 'flags', '')),
            }
            argument.update(self._proccess_kwargs(
                getattr(arg._value_, 'argparse_kwargs')))

            arg_type = getattr(arg._value_, 'type')
            argument['type'] = arg_type.__name__ if arg_type else ''
            argument['name'] = '' if argument['type'] == 'bool' else arg._name_

            if argument['required']:
                self.required_args.append(argument)
            else:
                self.optional_args.append(argument)
        return self

    def _proccess_kwargs(self, kwargs):
        def _process_choice(choices):
            return ', '.join([str(c) for c in choices] if choices else '')

        def _process_default(default):
            if isinstance(default, tuple) and isinstance(default[0], Path):
                default = default[0]
            if isinstance(default, Path):
                default = str(default).replace(str(Path.home()), '$HOME')
            return str(default)

        kwargs = kwargs if kwargs else {}
        return {
            'nargs': 'Yes' if kwargs.get('nargs', '') == '+' else '',
            'required': kwargs.get('required', True),
            'default': _process_default(kwargs.get('default', '')),
            'choices': _process_choice(kwargs.get('choices')),
        }


# docs/README.md
class MainPageDocumentationGenerator:
    def __init__(self, title, main_dir):
        self.title = title
        self.main_dir = main_dir

    def generate(self, tools):
        os.makedirs(self.main_dir, exist_ok=True)
        md = MdUtils(file_name=f'{self.main_dir}/README', title=self.title)
        Writer(md).write_tools_table(tools)
        md.create_md_file()


class ToolDocumentationGenerator:
    def __init__(self, tool, main_dir):
        self.tool = tool
        self.tool_name = tool.__name__
        self.tool_prefix = f'{main_dir}/{self.tool_name}'

    def generate(self):
        class_args_serializer = ArgumentsSerializer(self.tool.CLASS_ARGUMENTS).serialize()
        self.tool_optional_args = class_args_serializer.optional_args
        self.tool_serialized_actions = self._serialize_actions()
        self.tool_options = self._serialize_default_options()

        # docs/<tool-name>.md
        md = MdUtils(file_name=f'{self.tool_prefix}', title=self.tool_name)
        writer = Writer(md)
        writer.write_tool_command_usage(self)
        writer.write_description(self.tool.__doc__)
        writer.write_options(self.tool_options)
        writer.write_arguments(self.tool_name, self.tool_optional_args, [])
        writer.write_actions_table(self.tool_name, self.tool_serialized_actions)
        md.create_md_file()

        for action in self.tool_serialized_actions:
            # docs/<tool-name>_<action-name>.md
            md = MdUtils(file_name=f'{self.tool_prefix}_{action["name"]}', title=action['name'])
            writer = Writer(md)
            writer.write_action_command_usage(self, action)
            writer.write_description(action['description'])
            writer.write_options(self.tool_options)
            writer.write_arguments(f'command {action["name"]}', action['optional_args'], action['required_args'])
            writer.write_arguments(self.tool_name, self.tool_optional_args, [])
            md.create_md_file()

    def _serialize_actions(self):
        serialized_actions = []
        for f in self.tool.get_class_cli_actions():
            action_args_serializer = ArgumentsSerializer(f.arguments).serialize()
            serialized_actions.append({
                'action_name': f.action_name,
                'name': f.__name__,
                'description': f.__doc__,
                'required_args': action_args_serializer.required_args,
                'optional_args': action_args_serializer.optional_args,
            })
        return serialized_actions

    def _serialize_default_options(self):
        import argparse
        from codemagic.cli.cli_help_formatter import CliHelpFormatter

        def _serialize_option(option):
            return {
                'flags': ', '.join(option.option_strings),
                'description': str_plain(option.help),
                'choices': ', '.join(option.choices) if option.choices else '',
                'name': '',
                'default': '',
                'nargs': False,
                'required': False,
                'type': '',
            }

        parser = argparse.ArgumentParser(description=self.tool.__doc__, formatter_class=CliHelpFormatter)
        self.tool.get_default_cli_options(parser)
        possible_arguments = parser._actions
        return [_serialize_option(arg) for arg in possible_arguments]


class CommandUsageGenerator:
    def __init__(self, doc_generator):
        self.doc_generator = doc_generator
        self.tool_name = self._get_tool_name()

    def get_tool_command_usage(self):
        return f'{self.tool_name} {self._get_tool_flags()} ACTION'

    def get_action_command_usage(self, action):
        from pprint import pprint
        tool_flags = self._get_tool_flags()
        optional_flags = self._prepare_arguments(action['optional_args'])
        required_flags = self._prepare_arguments(action['required_args'])
        return f'{self.tool_name} {action["action_name"]} {tool_flags} {optional_flags} {required_flags}'

    def _get_tool_flags(self):
        optional_common_flags = self._prepare_arguments(self.doc_generator.tool_options)
        tool_flags = self._prepare_arguments(self.doc_generator.tool_optional_args)
        return f'{optional_common_flags} {tool_flags}'

    def _get_tool_name(self):
        tool_names = {
            'AppStoreConnect': 'app-store-connect',
            'GitChangelog': 'git-changelog',
            'Keychain': 'keychain',
            'UniversalApkGenerator': 'universal-apk',
            'XcodeProject': 'xcode-project'
        }
        return tool_names[self.doc_generator.tool.__name__]

    def _get_formatted_flag(self, arg):
        flag = f'{arg["flags"].split(",")[0]}'
        if not arg['flags'] and arg['name']:
            flag = arg['name']
        elif arg['choices'] and not arg['name']:
            flag = f'{flag} CHOSEN_OPTION'
        elif arg['name']:
            flag = f'{flag} {arg["name"]}'
        return flag if arg['required'] else f'[{flag}]'

    def _prepare_arguments(self, args):
        return ' '.join([self._get_formatted_flag(arg) for arg in args])


class Writer:
    def __init__(self, file):
        self.file = file

    def write_description(self, content):
        content = str_plain(content)
        self.file.new_header(level=4, title=content)

    def write_tool_command_usage(self, documentation_generator):
        content = CommandUsageGenerator(documentation_generator).get_tool_command_usage()
        self.file.new_paragraph(f"``{content}``")

    def write_action_command_usage(self, documentation_generator, action):
        content = CommandUsageGenerator(documentation_generator).get_action_command_usage(action)
        self.file.new_paragraph(f"``{content}``")

    def write_table(self, content, header):
        flat_content = sum(content, [])
        table = Table().create_table(
            columns=len(header),
            rows=len(content) + 1,
            text=header + flat_content,
            text_align='left'
        )
        self.file.write(table)

    def write_tools_table(self, tools):
        tools_source = [
            [
                f'[{tool.__name__}]({tool.__name__}.md)',
                str_plain(tool.__doc__)
            ] for tool in tools]
        self.write_table(tools_source, ['Tool name', 'Description'])

    def write_actions_table(self, tool_name, actions):
        self.file.new_header(level=3, title='Actions')
        actions_source = [
            [
                f'[{action["name"]}]({tool_name}_{action["name"]}.md)',
                str_plain(action['description'])
            ] for action in actions]
        self.write_table(actions_source, ['Action', 'Description'])

    def write_arguments(self, obj, optional, required):
        if required:
            self._write_arguments(f'Required arguments for {obj}', required)
        self._write_arguments(f'Optional arguments for {obj}', optional)

    def write_options(self, options):
        self._write_arguments(f'Optional arguments', options)

    def _write_arguments(self, title, args):
        def _process_flag(arg):
            flag = arg['flags']
            if flag and arg['choices']:
                return f'{flag}={{{arg["choices"]}}}'
            if flag and arg['name']:
                return f'{flag}={arg["name"]}'
            return arg['name'] if arg['name'] else flag

        def _process_description(arg):
            description = arg['description']
            description += f'. Type `{arg["type"]}`' if arg['type'] and arg['type'] != 'bool' else ''
            description += '. Multiple arguments' if arg['nargs'] else ''
            return f'{description}. Default: `{arg["default"]}`' if arg['default'] else description

        if not args:
            return
        
        self.file.new_header(level=3, title=title)
        for arg in args:
            flag = _process_flag(arg)
            description = _process_description(arg).replace('..','.')
            self.file.new_paragraph(f'**{flag}**')
            self.file.new_paragraph(description)


def str_plain(string):
    return re.compile('(\\x1b\[\d*m|\\x1b\[\d*m|\\n|\\t)').sub('', string).strip()


def main():
    main_dir = 'docs'
    tools = cli.CliApp.__subclasses__()
    MainPageDocumentationGenerator('CLI tools', main_dir).generate(tools)
    for tool in tools:
        ToolDocumentationGenerator(tool, main_dir).generate()


if __name__ == "__main__":
    main()
