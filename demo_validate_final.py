import pprint
import json
import re
from datetime import datetime
import copy

# ["decimal-100", "digit-200", "list-300", "exact_enum-400", "string-500", "boolean-600", "alphanum-700", "timestamp-800", "date-900", "conditional_key_validate-1000", "email=1100", "phone-1200", "length-1300", "required-1400"]
validation_list = ["decimal", "digit", "list", "exact_enum", "string", "boolean", "alphanum", "timestamp", "date", "conditional_key_validate", "email", "phone"]
default = "00"


class ValidationError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


class Validation(object):
    # def __init__(self, config_file):
    #     self.config_file = config_file

    def length_required_checker(self, type, key, value, source_dict):
        if 'length' in value:
            if isinstance(source_dict, list):
                for i in range(len(source_dict)):
                    self.length(key, value[7:-1], source_dict[i].get(key))
        else:
            if isinstance(source_dict, list):
                for i in range(len(source_dict)):
                    self.required(key, value, source_dict[i].get(key))

    def format_checker(self, type, key, value, source_dict):
        if '(' in value:
            if isinstance(source_dict, list):
                for i in range(len(source_dict)):
                    getattr(self, type)(key, value, source_dict[i].get(key))
        else:
            raise ValidationError(int(default), "format is not correct")

    def check_length(self, input):
        list1 = input.split(',')
        length = 0
        if len(list1) == 1:
            error_code = list1[0]
        else:
            length = list1[0]
            error_code = list1[1]
        return length, error_code

    def string(self, key, value, source_dict, multi=0):
        length, error_code = self.check_length(value[7:-1])
        if isinstance(source_dict, str):
            if length != 0:
                self.length(key, value[7:-1], source_dict)
        else:
            raise ValidationError(int(error_code), "'{}' is not a string".format(key))

    def exact_enum(self, key, value, source_dict):
        params = value[11:-1]
        list1 = params.split(']')
        params = list1[0]
        error_code = list1[1]
        if '[' in params:
            list1 = params[1:].split(',')
            if isinstance(source_dict, list):
                source_dict = list(source_dict)
                for i in source_dict:
                    if i in list1:
                        pass
                    else:
                        raise ValidationError(int(error_code[2:]), "'{}' is not exact enum".format(key))
            else:
                params = params[1:]
                if source_dict == params:
                    pass
                else:
                    raise ValidationError(int(error_code[2:]), "'{}' is not exact enum".format(key))
        else:
                raise ValidationError(int(default), "format is not correct")

    def boolean(self, key, value, source_dict):
        length, error_code = self.check_length(value[8:-1])
        if isinstance(source_dict, bool):
            if length != 0:
                self.length(key, value[8:-1], source_dict)
        else:
            raise ValidationError(int(error_code), "'{}' is not boolean".format(key))

    def length(self, key, length, source_dict):
        length, error_code = self.check_length(length)
        source_dict = str(source_dict)
        if len(source_dict) == int(length):
            pass
        else:
            raise ValidationError(int(error_code), "length of '{}' is not {}".format(key, length))

    def notrequired(self, key, value, source_dict):
        length, error_code = self.check_length(value[12:-1])
        if source_dict is None:
            pass
        else:
            raise ValidationError(int(error_code), "'{}' is present".format(key))

    def digit(self, key, value, source_dict):
        length, error_code = self.check_length(value[6:-1])
        source_dict = str(source_dict)
        if source_dict.isdigit():
            if length != 0:
                self.length(key, value[6:-1], source_dict)
        else:
            raise ValidationError(int(error_code), "'{}' is not a number".format(key))

    def alphanum(self, key, value, source_dict):
        length, error_code = self.check_length(value[9:-1])
        source_dict = str(source_dict)
        if source_dict.isalnum():
            if length != 0:
                self.length(key, value[9:-1], source_dict)
        else:
            raise ValidationError(int(error_code), "'{}' is not alphanumeric".format(key))

    def decimal(self, key, value, source_dict):
        length, error_code = self.check_length(value[8:-1])
        try:
            source_dict = float(source_dict)
        except Exception as e:
            raise ValidationError(int(error_code), "'{}' is not decimal".format(key))
        if isinstance(source_dict, float):
            pass
        else:
            raise ValidationError(int(error_code), "'{}' value is not decimal".format(key))

    def list(self, key, value, source_dict):
        length, error_code = self.check_length(value[5:-1])
        if isinstance(source_dict, list):
            pass
        else:
            raise ValidationError(int(error_code), "'{}' is not list".format(key))

    def required(self, key, value, source_dict, multi=0):
        length, error_code = self.check_length(value[9:-1])
        if source_dict:
            pass
        else:
            raise ValidationError(int(error_code), "for '{}' value is not present".format(key))

    def email(self, key, value, source_dict):
        if '(' in value:
            length, error_code = self.check_length(value[6:-1])
            if re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$', source_dict):
                pass
            else:
                raise ValidationError(int(error_code), "'{}' is not a valid email id".format(key))
        else:
            raise ValidationError(int(default), "format is not correct")

    def date(self, key, value, source_dict):
        if '(' in value:
            date_format, error_code = self.check_length(value[5:-1])
            try:
                datetime.strptime(source_dict, date_format)
            except Exception:
                raise Exception(int(error_code), "'{}' format doesn't match with '{}'".format(key, date_format))
        else:
            raise ValidationError(int(default), "format is not correct")

    def timestamp(self, key, value, source_dict):
        pass

    def phone(self, key, value, source_dict):
        if '(' in value:
            length, error_code = self.check_length(value[6:-1])
            if re.match(r'[789]\d{9}$', str(source_dict)):
                pass
            else:
                raise ValidationError(int(error_code), "'{}' is not a valid phone number".format(key))
        else:
            raise ValidationError(int(default), "format is not correct")

    def multi_validator(self, key, value, source_dict):
        for i in value:
            if "required" in i:
                self.required(key, i, source_dict)
            elif "length" in i:
                self.length(key, i[7:-1], source_dict)
            else:
                list1 = i.split(',')
                if len(list1) == 1:
                    a = i.index('(')
                    getattr(Validation, i[0:a])(self, key, i, source_dict)
                else:
                    getattr(self, i[0:-8])(key, i, source_dict)

    def read_config(self, config_dict, source_dict):
        if isinstance(config_dict, dict):
            for key, value in config_dict.items():
                if isinstance(value, dict):
                    self.read_config(value, source_dict.get(key))
                elif isinstance(value, list):
                    # for j in value:
                    if isinstance(value[0], str):
                        demo_source_dict = copy.deepcopy(source_dict)
                        for i in value:
                            if isinstance(i, dict):
                                if "include" in i:
                                    index = i.get('include', [])
                                    demo_source_dict = []
                                    for k in index:
                                        demo_source_dict.append(source_dict[k])
                                elif "exclude" in i:
                                    index = i.get('exclude', [])
                                    # demo_source_dict = source_dict
                                    for k in index:
                                        demo_source_dict.remove(demo_source_dict[k])
                                # else:
                                #     demo_source_dict = source_dict
                                z = 0
                                for item in validation_list:
                                    if "length" in value[z]:
                                        self.length_required_checker('length', key, value[z], demo_source_dict)
                                        z += 1
                                    elif "required" in value[z]:
                                        self.length_required_checker('required', key, value[z], demo_source_dict)
                                        z += 1
                                    elif item in value[z]:
                                        self.format_checker(item, key, value[z], demo_source_dict)
                                        z += 1
                        # self.multi_validator(key, value, demo_source_dict[index].get(key))
                    else:
                        for i in range(len(value)):
                            self.read_config(value[i], source_dict.get(key))
                elif isinstance(value, int):
                    self.fail_list.append(key)
                elif isinstance(value, str):
                    if "notrequired" in value:
                        if key:
                            self.notrequired(key, value, source_dict.get(key))
                        else:
                            pass
                    elif "required" in value:
                        self.length_required_checker('required', key, value, source_dict)
                        # self.required(key, value, source_dict.get(key))
                    elif "length" in value:
                        self.length_required_checker('length', key, value, source_dict)
                        # self.length(key, value[7:-1], source_dict.get(key))
                    else:
                        for item in validation_list:
                            if item in value:
                                index = 0
                                if isinstance(value, list):
                                    for i in value:
                                        if isinstance(i, list):
                                            index = i[0]
                                            value.remove(i)
                                self.format_checker(item, key, value, source_dict)
                                # getattr(Validation, item)(self, key, value, source_dict.get(key))
                                break
        elif isinstance(config_dict, list):
            for item in config_dict:
                pass

    def start_validate(self, config_file, source_file):
        config_dict = json.loads(open(config_file, 'r').read())
        source_dict = json.loads(open(source_file, 'r').read())
        self.read_config(config_dict, source_dict)


if __name__ == '__main__':
    v = Validation()
    v.start_validate("C:\\Users\\senguptaa\\Desktop\\AyanJson_demo\\source_data\\validation_config.json", "C:\\Users\\senguptaa\\Desktop\\AyanJson_demo\\demo_final_directory\\output.json")
    # pprint.PrettyPrinter(indent=4).pprint(v.pass_list)
    # pprint.PrettyPrinter(indent=4).pprint(v.fail_list)
