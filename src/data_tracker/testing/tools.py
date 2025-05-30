def gen_yield_line_numbers():
    value_to_add = 50
    i = -1
    while True:
        # for i in range(30):
        i += 1
        yield {"skiprows": i * value_to_add, "nrows": value_to_add}


def create_data_generator_for_testing():
    state = {"gen": gen_yield_line_numbers(), "last_value": None}

    def get_new_data():
        try:
            state["last_value"] = next(state["gen"])
            print(state["last_value"])
            return state["last_value"]
        except StopIteration:
            return state["last_value"]  # Return last valid value when exhausted

    return get_new_data


# get_new_data = create_data_generator(dict_global)

# gen_yield_line = gen_yield_line_numbers()

# def get_new_data():
#     return next(gen_yield_line)
