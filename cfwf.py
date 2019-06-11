import pandas as pd

def read_cfwf(filepath_or_buffer, type_width, colspecs, names=None,
              dtype=None, chunksize=None, nrows=None, compression='infer',
              encoding=None):
    '''Read complex fixed-width formatted lines, which are fixed-width formatted
    files with different line types, each one possibly having different
    colspecs, names and dtypes. Returns a dict of line type -> pandas.DataFrame.

    Also supports optionally breaking of the file into chunks.

    Arguments:
    filepath_or_buffer -- str, pathlib.Path, py._path.local.LocalPath or any
        object with a read() method (such as a file handle or StringIO).
    type_width -- int
        Number of characters indicating the line type in the beginning of each 
        line.
    colspecs -- dict of line type -> list of pairs (int, int).
        A dict of list of pairs (tuples) giving the extents of the fixed-width
        fields of each line as half-open intervals (i.e., [from, to[ ), for each
        line type. The line types included in the colspecs indicates which line 
        types are supposed to be read. Lines with other types will be ignored.
    names -- dict of line type -> list, default None
        dict of list of column names to use, one list for each line type.
    dtype -- dict of line type -> dict of column -> type, default None
        Data type for columns, for each line type. If not specified for a
        specific column, data will be kept as str.
    chuncksize -- int, default None
        If specified, break the file into chunks and returns a generator.
    nrows -- int, default None
        Limit the number of lines to be read.
    '''

    # Calculate line width as the maximum 
    # position number from the colspecs.
    line_width = max([max(colspec)[1] for colspec in colspecs.values()])

    # Read raw file as a two column dataframe, one column for the line type
    # and the other column for the line content (to be split later).
    raw_data = pd.read_fwf(filepath_or_buffer,
                           colspecs=[(0,type_width),(type_width,line_width)],
                           names=['line_type','_content'],
                           dtype=str,
                           header=None,
                           delimiter='\t', # To avoid autostrip content
                           chunksize=chunksize,
                           nrows=nrows,
                           compression=compression,
                           encoding=encoding)

    if chunksize is None:
        return _cfwf_chunck(raw_data, 
                            type_width, 
                            colspecs, 
                            names, 
                            dtype)
    else:
        return _cfwf_chunck_reader(raw_data, 
                                   type_width, 
                                   colspecs, 
                                   names, 
                                   dtype)


def _cfwf_chunck(df, type_width, colspecs, names=None, dtype=None):

    df.set_index('line_type', inplace=True)

    data_dict = {}
    
    # For each line type specified in colspecs.
    for ltype, specs in colspecs.items():
        try:
            # Get all rows corresponding to the line type.
            data = df.loc[[ltype],:].copy()

            # Create columns spliting content according to colspecs.
            for i, column in enumerate(specs):
                data[i] = (data['_content']
                            .str.slice(column[0]-type_width, 
                                       column[1]-type_width)
                            .str.strip())

            # Original content column not necessary anymore.
            data_dict[ltype] = data.drop('_content', axis=1)

            # Change column names according to parameter "names".
            if names is not None:
                data_dict[ltype].columns = names[ltype]

            # If dtypes specified and only if specified 
            # for this specific line type.
            if (dtype is not None) & (ltype in dtype):
                # Change column dtypes according to parameter "dtype"
                for col_name, col_type in dtype[ltype].items():
                    data_dict[ltype][col_name] = (data_dict[ltype][col_name]
                                                    .astype(col_type))

        except KeyError:
            pass

    return data_dict    

def _cfwf_chunck_reader(reader, type_width, colspecs, names=None, dtype=None):

    for chunk in reader:
        yield _cfwf_chunck(chunk, type_width, colspecs, names, dtype)
