#!/usr/bin/env python3
import os
import pandas as pd

def read_log_file(filename):
    """
    Read a single LAMMPS log file.
    Skips lines starting with '==>' and blank lines.
    The first non-comment line (starting with a letter) is assumed to be the header.
    """
    data_lines = []
    header = None
    with open(filename, 'r') as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("==>"):
                continue
            # Treat the first line starting with an alphabet as the header.
            if header is None and line_strip.split()[0][0].isalpha():
                header = line_strip
                data_lines.append(header)
            else:
                data_lines.append(line_strip)
    from io import StringIO
    data_str = "\n".join(data_lines)
    df = pd.read_csv(StringIO(data_str), delim_whitespace=True)
    return df

def combine_log_files_with_offset(file_list):
    """
    Combine multiple log files in the given order.
    For each file, compute a new column "convert_simTime" 
    as the cumulative offset of the original v_simTime.
    The original v_simTime remains unchanged.
    Also add a 'source_file' column for later identification.
    """
    cumulative_offset = 0.0
    df_list = []
    for file in file_list:
        try:
            df = read_log_file(file)
            if 'v_simTime' not in df.columns:
                print(f"File {file} does not contain 'v_simTime' column. Skipping.")
                continue
            # 計算新的時間欄位 convert_simTime = v_simTime + cumulative_offset
            df["convert_simTime"] = df["v_simTime"] + cumulative_offset
            # 更新 cumulative_offset 使用剛剛計算出的 convert_simTime 中的最大值
            cumulative_offset = df["convert_simTime"].max()
            df["source_file"] = os.path.basename(file)
            df_list.append(df)
            print(f"Read {file}: new convert_simTime range: {df['convert_simTime'].min()} - {df['convert_simTime'].max()}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    if df_list:
        df_all = pd.concat(df_list, ignore_index=True, sort=False)
    else:
        df_all = pd.DataFrame()
    return df_all

def main():
    # 請根據實際情況修改 log 文件清單
    log_files = ['log-1.txt', 'log-2.txt', 'log-3.txt', 'log-4.txt', 'log-5.txt']
    
    df_all = combine_log_files_with_offset(log_files)
    if df_all.empty:
        print("No log data combined. Please check file contents and paths.")
        return
    
    output_csv = "combined_data.csv"
    df_all.to_csv(output_csv, index=False)
    print(f"Combined log data saved to {output_csv}")

if __name__ == "__main__":
    main()

