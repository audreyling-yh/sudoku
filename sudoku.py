import pandas as pd
pd.set_option('display.max_columns', 9)
import itertools

class Sudoku:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.single_count = 0

    def solve(self):
        df = self.parse()
        possible_df = self.get_possible_values(df)

        self.single_count = possible_df.applymap(self.check_single_list).values.sum()
        while self.single_count != 0:
            possible_df = self.fill_singles(possible_df)
            possible_df = self.fill_unique_col_vals(possible_df)
            possible_df = self.fill_unique_row_vals(possible_df)
            possible_df = self.fill_unique_cube_values(possible_df)

        self.get_unfilled_loc(possible_df)
        if len(self.unfilled_locs) > 0:
            possible_df = self.reset_unfilled(possible_df)

        print(possible_df)
        return possible_df


    def recurse(self, df, i, j):
        val = df[i, j]
        fill_value = 1
        if val == 0:
            existing_rowvals = [x for x in df.iloc[i].tolist() if type(x) != list]
            existing_colvals = [x for x in df[j] if type(x) != list]
            existing_cubevals = self.get_cube_values(df, i, j)
            existing_vals = existing_rowvals + existing_colvals + existing_cubevals
            if fill_value in existing_vals and fill_value < 9:
                fill_value += 1
            elif fill_value in existing_vals and fill_value == 9:
                return False
            else:
                df[i, j] = fill_value
                if i != 8:
                    i += 1
                    self.recurse(df, i, j)
                elif i == 8:
                    i = 0
                    j += 1
                    self.recurse(df, i , j)





    def reset_unfilled(self, df):
        for pos in self.unfilled_locs:
            i = pos[0]
            j = pos[1]
            df.loc[i, j] = 0
        return df

    def get_unfilled_loc(self, df):
        self.unfilled_locs = []
        for i, j in itertools.product(range(0, 9), range(0, 9)):
            value = df.loc[i, j]
            if type(value) == list:
                self.unfilled_locs.append((i, j))

    def get_random_possibility(self, df, i, j):
        val = df.loc[i, j]
        existing_rowvals = [x for x in df.iloc[i].tolist() if type(x) != list]
        existing_colvals = [x for x in df[j] if type(x) != list]
        existing_cubevals = self.get_cube_values(df, i, j)
        existing_vals = existing_rowvals + existing_colvals + existing_cubevals

        possibilities = [x for x in val if x not in existing_vals]
        return possibilities


    def fill_unique_cube_values(self, df):
        for i, j in itertools.product([0, 3, 6], [0, 3, 6]):
            cube_values = self.get_cube_values(df, i, j, exclude_ij = True)
            confirmed_vals = self.get_unique_possibility(cube_values)
            cube_i = self.get_cube_indexes(i)
            cube_j = self.get_cube_indexes(j)

            if len(confirmed_vals) != 0:
                for x in confirmed_vals:
                    for x, y in itertools.product(cube_i, cube_j):
                        val = df.loc[i, j]
                        if type(val) == list and x in val:
                            df.loc[i, j] = x
                            df = self.drop_from_possibility(df, i, j, x)
        self.single_count = df.applymap(self.check_single_list).values.sum()
        return df


    def fill_unique_row_vals(self, df):
        for i in range(0,9):
            row = df.iloc[i]
            confirmed_vals = self.get_unique_possibility(row)
            if len(confirmed_vals) != 0:
                for x in confirmed_vals:
                    for j in range(0, len(row)):
                        val = row[j]
                        if type(val) == list and x in val:
                            df.loc[i, j] = x
                            df = self.drop_from_possibility(df, i, j, x)
        self.single_count = df.applymap(self.check_single_list).values.sum()
        return df


    def fill_unique_col_vals(self, df):
        for j in range(0,9):
            col = df[j]
            confirmed_vals = self.get_unique_possibility(col)
            if len(confirmed_vals) != 0:
                for x in confirmed_vals:
                    for i in range(0, len(col)):
                        val = col[i]
                        if type(val) == list and x in val:
                            df.loc[i, j] = x
                            df = self.drop_from_possibility(df, i, j, x)
        self.single_count = df.applymap(self.check_single_list).values.sum()
        return df


    def get_unique_possibility(self, values):
        unconfirmed_vals = [(x for x in val) for val in values if type(val) == list]
        confirmed_vals = [x for x in unconfirmed_vals if unconfirmed_vals.count(x) == 1]
        return confirmed_vals

    def fill_singles(self, df):
        for i, j in itertools.product(range(0,9), range(0,9)):
            value = df.loc[i, j]
            if type(value) == list and len(value) == 1:
                df.loc[i, j] = value[0]
                df = self.drop_from_possibility(df, i, j, value[0])
        self.single_count = df.applymap(self.check_single_list).values.sum()
        return df


    def drop_from_possibility(self, df, i, j, filled_value):
        row = df.iloc[i]
        for c in range(0, 9):
            val = row[c]
            if type(val) == list and filled_value in val:
                df.loc[i, c].remove(filled_value)

        col = df[j]
        for r in range(0, 9):
            val = col[r]
            if type(val) == list and filled_value in val:
                df.loc[r, j].remove(filled_value)

        cube_i = self.get_cube_indexes(i)
        cube_j = self.get_cube_indexes(j)
        for x, y in itertools.product(cube_i, cube_j):
            val = df.loc[x, y]
            if type(val) == list and filled_value in val:
                df.loc[x, y].remove(filled_value)

        return df


    def get_possible_values(self, df):
        copy = df.copy()

        for i, j in itertools.product(range(0,9), range(0,9)):
            value = df.loc[i, j]
            if value == 0:
                existing_rowvals = [x for x in df.iloc[i].tolist() if x != 0]
                existing_colvals = [x for x in df[j] if x != 0]
                existing_cubevals = self.get_cube_values(df, i, j)
                existing_vals = existing_rowvals + existing_colvals + existing_cubevals

                possible_vals = [x for x in list(range(1, 10)) if x not in existing_vals]
                copy.loc[i, j] = possible_vals
        return copy


    def get_cube_values(self, df, i, j, exclude_ij = True):
        cube_i = self.get_cube_indexes(i)
        cube_j = self.get_cube_indexes(j)

        if exclude_ij:
            existing_vals = [df.loc[x, y] for x, y in itertools.product(cube_i, cube_j) if x != i and y != j]
        else:
            existing_vals = [df.loc[x, y] for x, y in itertools.product(cube_i, cube_j)]

        existing_vals = [x for x in existing_vals if x != 0 and type(x) != list]
        return existing_vals

    def get_cube_indexes(self, row_or_col_index):
        if row_or_col_index in [0, 3, 6]:
            indexes = list(range(row_or_col_index, row_or_col_index + 3))
        elif row_or_col_index in [1, 4, 7]:
            indexes = list(range(row_or_col_index - 1, row_or_col_index + 2))
        elif row_or_col_index in [2, 5, 8]:
            indexes = list(range(row_or_col_index - 2, row_or_col_index + 1))
        return indexes


    def parse(self):
        data = [int(x) for x in list(self.puzzle)]
        data = zip(*[iter(data)] * 9)
        df = pd.DataFrame(data).astype('object')
        return df

    def check_single_list(self, value):
        if type(value) == list and len(value) == 1:
            result = True
        else:
            result = False
        return result

if __name__ == '__main__':
    # # data from https://www.kaggle.com/bryanpark/sudoku
    # data = pd.read_csv('data/sudoku.csv', encoding = 'utf-8')
    #
    # correct_count = 0
    # for i in range(1000):
    #     puzzle = data['quizzes'].iloc[i]
    #     solution = data['solutions'].iloc[i]
    #
    #     sd = Sudoku(puzzle)
    #     result = sd.solve()
    #     # print(result)
    #     answer = ''.join([str(x) for x in list(result.values.flat)])
    #
    #     if answer == solution:
    #         correct_count += 1
    #     else:
    #         print(i)
    #         print(result)
    #         print('WRONG')
    # print(correct_count)

    puzzle = '800000000003600000070090200050007000000045700000100030001000068008500010090000400'
    sd = Sudoku(puzzle)
    res = sd.solve()
    # print(res)








