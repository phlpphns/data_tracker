import traceback


def create_data_generator_real(dict_global):
    """
    return kwargs???
    this function is bad because of len(None)
    """
    # print('inside create_data_generator_real')
    try:
        # dict_ = {"skiprows": 0}
        dict_ = {
            "skiprows": len(dict_global.get("pandas_main_dataframe_read_data", None))
        }
        # print(dict_)
        return dict_
    except:
        print("error in generator function")
        traceback.print_exc()
        return {"skiprows": 0}
