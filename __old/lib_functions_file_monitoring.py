# def data_feeder():
#         problem potentially: data format not fixed? can we press each input into a scheme? columns, arrays ... ?
#         refresh_feature_checkboxes
#         convert_time_stamp

#         pass





def detect_file_type(path_):
    if not dict_global["file_type", "csv"]:
        file_type = os.path.splitext(path_)[-1]
    print(f"the detected file type is: {file_type}")
    return file_type





