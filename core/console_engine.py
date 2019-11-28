#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Pygments Package
from core.console_accounts import ConsoleAccounts
from core.utils.contract.contract_syntax_lexer import ContractSyntaxLexer
from core.utils.contract.contract_method_completer import ContractMethodCompleter
from core.utils.contract.contract_console_artifacts import ContractConsoleArtifacts
from core.utils.contract.contract_payload_artifacts import ContractPayloadArtifacts

# Import PromptToolkit Package
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession


# Import Os Package
import os

# style = Style.from_dict({
#     'completion-menu.completion': 'bg:#008888 #ffffff',
#     'completion-menu.completion.current': 'bg:#00aaaa #000000',
#     'scrollbar.background': 'bg:#88aaaa',
#     'scrollbar.button': 'bg:#222222',
# })


from prompt_toolkit.styles import Style
from core.console_input_getter import ConsoleInputGetter
from core.utils.contract.contract_payload_artifacts import ContractPayloadArtifacts
from core.utils.contract.console_help import ConsoleInformation
from core.utils.contract.console_safe_methods import ConsoleSafeMethods

# todo: move to constants class
QUOTE = '\''
COMA = ','
PROJECT_DIRECTORY = os.getcwd() + '/assets/safe-contracts-1.1.0/'

from core.utils.contract.contract_method_artifacts import ContractMethodArtifacts

class GnosisConsoleEngine:
    def __init__(self):
        self.name = self.__class__.__name__
        self.console_session = PromptSession()
        self.previous_session = None

        self.prompt_text = 'GNOSIS-CLI v0.0.1a'
        self.network = 'ganache'

        self.console_accounts = ConsoleAccounts()
        self.console_payloads = ContractPayloadArtifacts()
        self.console_artifacts = ContractConsoleArtifacts()
        self.console_information = ConsoleInformation()
        self.console_getter = ConsoleInputGetter()

        self.default_auto_fill = False
        self.default_owner = ''
        self.default_owner_list = []

        self.session_config = {
            'prompt': self._get_prompt_text(stream=self.prompt_text),
            'contract_lexer': ContractSyntaxLexer(),
            'contract_completer': ContractMethodCompleter(),
            'gnosis_lexer': None,
            'style': 'Empty',
            'completer': WordCompleter(
                [
                    'about', 'info', 'help', 'newContract', 'loadContract', 'setNetwork', 'viewNetwork',
                    'close', 'quit', 'viewContracts', 'viewAccounts', 'newAccount', 'setAutofill',
                    'viewPayloads', 'newPayload', 'newTxPayload', 'setDefaultOwner', 'setDefaultOwnerList',
                    'viewOwner', 'viewOwnerList', 'dummyCommand', 'loadSafe'
                 ],
                ignore_case=True)
        }

    def run_console_session(self, prompt_text='', previous_session=None, contract_methods=None, contract_instance=None, safe_interface=None):
        """ Run Console Session

        :param prompt_text:
        :param previous_session:
        :param contract_methods:
        :param contract_instance:
        :return:
        """
        session = self.get_console_session(prompt_text, previous_session)
        try:
            while True:
                try:
                    # remark: Start the prompt
                    stream = session.prompt()
                    if previous_session is None:
                        # remark: eval gnosis-cli arguments
                        self.operate_with_console(stream, session)
                    else:
                        # remark: eval contract-cli arguments
                        if safe_interface is not None:
                            print('entra en safe')
                            safe_interface.operate_with_safe(stream)
                        else:
                            self.operate_with_contract(stream, contract_methods, contract_instance)
                    # remark: If you are in a sub session of the console return to gnosis-cli session
                    command_argument, argument_list = self.console_getter._get_input_console_arguments(stream)
                    if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
                        return self.close_console_session(previous_session)
                except KeyboardInterrupt:
                    continue  # remark: Control-C pressed. Try again.
                except EOFError:
                    break  # remark: Control-D pressed.
        except Exception as err:
            print('FATAL:', type(err), err)

    def get_console_session(self, prompt_text='', previous_session=None):
        """ Get Console Session

        :param prompt_text:
        :param previous_session:
        :return:
        """
        if previous_session is None:
            return PromptSession(self.session_config['prompt'], completer=self.session_config['completer'], lexer=self.session_config['contract_lexer'])
        else:
            return PromptSession(prompt_text, completer=self.session_config['contract_completer'], lexer=self.session_config['contract_lexer'])

    @staticmethod
    def close_console_session(previous_session=None):
        """ Close Console Session
        This function will return the previous session otherwise it will exit the gnosis-cli
        :param previous_session:
        :return:
        """
        if previous_session is None:
            raise EOFError
        return previous_session

    def load_contract_artifacts(self, contract_artifacts):
        """ Load Contract Artifacts

        :param contract_artifacts:
        :return:
        """
        self.contract_artifacts = contract_artifacts
        # remark: Pre-Loading of the Contract Assets (Safe v1.1.0, Safe v1.0.0, Safe v-0.0.1)
        # remark: Map the Artifacts of the Assets
        # note: method 1, with alias
        self.console_artifacts.add_artifact(contract_artifacts, alias=contract_artifacts['name'])
        # note: method 2, wihout alias
        for contract_artifacts_item in [contract_artifacts]:
            self.console_artifacts.add_artifact(contract_artifacts_item)
        print('Pre-Loading Done.')
        print('+' + '---------' * 10 + '+')

    def command_set_network(self, value):
        """ Command Set Network
        This function will perform the setNetwork functionality in the gnosis-cli
        :param value:
        :return:
        """
        self.network = value

    def command_set_default_owner(self, value):
        self.default_owner = value

    def command_set_default_owner_list(self, value):
        self.default_owner_list = value

    def command_view_default_owner_list(self):
        print('Default Owner List', self.default_owner_list)

    def command_view_default_owner(self):
        print('Default Owner:', self.default_owner)

    def command_view_network(self):
        print('Current_Network:', self.network)

    def command_load_safe(self, desired_parsed_item_list, priority_group, command_argument, argument_list, previous_session):
        print('Data:', desired_parsed_item_list, priority_group, command_argument, argument_list)
        if priority_group == 0:
            print('Do Nothing')
        elif priority_group == 1:
            tmp_address = desired_parsed_item_list[0][1][0]
            print()
            safe_interface = ConsoleSafeMethods(tmp_address)
            self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='./', stream='SafeTest(' + tmp_address + ')'),
                                    previous_session=previous_session, safe_interface=safe_interface)

    # note: Future command to it's own funciton
    def command_load_contract(self, desired_parsed_item_list, priority_group, command_argument, argument_list, previous_session):
        """ Command Load Contract

        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :param previous_session:
        :return:
        """
        print('Data:', desired_parsed_item_list, priority_group, command_argument, argument_list)
        if priority_group == 0:
            tmp_alias = desired_parsed_item_list[0][1][0]
            print('alias:', tmp_alias)
            try:
                contract_instance = self.console_artifacts.get_value_from_alias(tmp_alias, 'instance')
                contract_methods = ContractMethodArtifacts().map_contract_methods(contract_instance)
                self.run_console_session(prompt_text=self._get_prompt_text(affix_stream='./', stream=tmp_alias),
                                         previous_session=previous_session, contract_methods=contract_methods,
                                         contract_instance=contract_instance)
            except KeyError as err:
                print(command_argument, type(err), err)
        elif priority_group == 1:
            print(command_argument, argument_list)

    def operate_with_console(self, stream, previous_session):
        desired_parsed_item_list, priority_group, command_argument, argument_list = self.console_getter.get_gnosis_input_command_argument(stream)
        if command_argument == 'loadContract':
            self.command_load_contract(desired_parsed_item_list, priority_group, command_argument, argument_list, previous_session)
        elif command_argument == 'setNetwork':
            print('setNetwork')
            # self.command_set_network(self.console_getter.get_gnosis_input_command_argument(command_argument, argument_list))
        elif command_argument == 'viewNetwork':
            self.command_view_network()
        elif command_argument == 'viewContracts':
            self.console_artifacts.command_view_contracts()
        elif command_argument == 'viewAccounts':
            self.console_accounts.command_view_accounts()
        elif command_argument == 'viewPayloads':
            self.console_payloads.command_view_payloads()
        elif command_argument == 'about':
            self.console_information.command_view_about()
        elif (command_argument == 'info') or (command_argument == 'help'):
            self.console_information.command_view_help()
        elif command_argument == 'newAccount':
            # Add Ethereum money conversion for all types of coins
            print('newAccount <Address> or <PK> or <PK + Address>')
        elif command_argument == 'newPayload':
            self.console_payloads.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newTxPayload':
            self.console_payloads.command_new_payload(command_argument, argument_list)
        elif command_argument == 'setDefaultOwner':
            self.command_set_default_owner(argument_list)
        elif command_argument == 'setDefaultOwnerList':
            self.command_set_default_owner_list(argument_list)
        elif command_argument == 'setAutofill':
            print('Autofill Function')
        elif command_argument == 'viewOwner':
            self.command_view_default_owner()
        elif command_argument == 'viewOwners':
            self.command_view_default_owner_list()
        elif command_argument == 'dummyCommand':
            self.console_getter.get_gnosis_input_command_argument(stream)
        elif command_argument == 'loadSafe':
            self.command_load_safe(desired_parsed_item_list, priority_group, command_argument, argument_list, previous_session)

    def operate_with_contract(self, stream, contract_methods, contract_instance):
        """ Operate With Contract
        This function will retrieve the methods present in the contract_instance
        :param stream: command_argument (method to call) that will trigger the operation
        :param contract_methods: dict with all the avaliable methods retrieved from the abi file
        :param contract_instance: only for eval() so it can be triggered
        :return: if method found, a method from the current contract will be triggered, success or not depends on the establishing of the proper values.
        """
        try:
            # print('Call operate_with_contract:', stream)
            # print('Contract Methods', contract_methods)
            # print('Contract Instance', contract_instance)
            for item in contract_methods:
                if contract_methods[item]['name'] in stream:
                    splitted_stream = stream.split(' ')
                    function_name, function_arguments, address_from, execute_flag, queue_flag, query_flag = self.console_getter.get_input_method_arguments(
                        splitted_stream, contract_methods[item]['arguments'])
                    print('command:', function_name, 'arguments', function_arguments, 'tx:', execute_flag, 'call:', query_flag)
                    # print(self._get_input_method_arguments(splitted_stream, contract_methods[item]['arguments']))

                    if execute_flag or query_flag or queue_flag:

                        # remark: Transaction Solver
                        if execute_flag:
                            if contract_methods[item]['name'].startswith('get'):
                                print('WARNING: transact() operation is discourage and might not work if you are calling a get function')
                            # if address_from != '':
                                # address_from = '\{\'from\':{0}\}'.format(address_from)

                            print(contract_methods[item]['transact'].format(function_arguments, address_from))
                            print(eval(contract_methods[item]['transact'].format(function_arguments, address_from)))
                            # this is the hash to be signed, maybe call for approve dialog, approveHash dialogue,
                            # map functions to be performed by the gnosis_py library

                        # remark: Call Solver
                        elif query_flag:
                            print(contract_methods[item]['call'].format(function_arguments, address_from))
                            print(eval(contract_methods[item]['call'].format(function_arguments, address_from)))

                        # remark: Add to the Batch Solvere
                        elif queue_flag:
                            print(contract_methods[item]['call'].format(function_arguments, address_from))
                            print('INFO: executeBatch when you are ready to launch the transactions that you queued up!')
                    else:
                        print('WARNING: --execute, --query or --queue flag needed!')
        except Exception as err:
            print('here:!!', type(err), err)

    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text

        :param contract_name:
        :return:
        """
        if affix_stream == '':
            return '[ {cli_name} ]>: '.format(cli_name=self.prompt_text)
        return '[ {affix_stream} ][ {stream} ]>: '.format(affix_stream=affix_stream, stream=stream)
