import plot_functions
import pickle
file_name = 'question lists\\question_list.pkl'
# file_name = 'question lists\\question_list_July_23rd_all_exponential_with_decaying_factors_smaller_window_02.pkl'
# file_name = 'question lists\\question_list_beautiful_linear.pkl'
file_name = 'users\\tomer\\iteration_list.pkl'
with open(file_name, 'rb') as inp:
    iteration_list = pickle.load(inp)
plot_functions.my_plot(iteration_list=iteration_list, keys='white')