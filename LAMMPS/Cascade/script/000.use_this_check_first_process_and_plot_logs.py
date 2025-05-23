#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.linewidth': 2,
    'axes.titlesize': 12,
    'axes.labelsize': 12,
    'legend.fontsize': 13,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13
})
tick_params = {'direction': 'in', 'width': 2, 'length': 6}


def read_log_file(filename):
    data_lines = []
    header = None
    with open(filename, 'r') as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("==>"):
                continue
            if header is None and line_strip.split()[0][0].isalpha():
                header = line_strip
                data_lines.append(header)
            else:
                data_lines.append(line_strip)
    from io import StringIO
    data_str = "\n".join(data_lines)
    df = pd.read_csv(StringIO(data_str), sep='\s+')
    if df.isnull().values.any():
        print(f"Warning: NaN values found in {filename}. They will be filled with 0.")
        df.fillna(0, inplace=True)
    return df


def process_and_plot_individual_logs(file_list):
    cumulative_offset = 0
    for file in file_list:
        try:
            df = read_log_file(file)
            if 'v_simTime' not in df.columns:
                print(f"File {file} does not contain 'v_simTime' column. Skipping.")
                continue
            individual_csv = f"data-{os.path.splitext(file)[0]}.csv"
            df.to_csv(individual_csv, index=False)
            print(f"Individual log data saved to {individual_csv}")

            # Calculate breakpoints
            breakpoints = [cumulative_offset + 2540]
            cumulative_offset += df['Step'].max()

            fig, ax1 = plt.subplots(figsize=(8,6))
            ax1.plot(df['Step'], df['c_sys'],    color='green',    label='Whole  System Temp', linewidth=3)
            ax1.plot(df['Step'], df['c_ex'],    color='blue',      label='External Only Temp', linewidth=3)
            ax1.plot(df['Step'], df['c_in'],    color='red',       label='Internal Only Temp', linewidth=3)
            for bp in breakpoints:
                plt.axvline(x=bp, color='grey', linestyle='dashdot', linewidth=1)
            ax1.set_xlabel('Step')
            ax1.set_ylabel('Temp')
            ax1.set_xlim(df['Step'].min(), df['Step'].max())
            ax1.legend()
            ax1.tick_params(**tick_params)
            plt.tight_layout()
            plt.savefig(f"fig-step-Temperature-Evolution{os.path.splitext(file)[0]}.pdf", dpi=1200,transparent=True)
            plt.close()

            plt.figure(figsize=(8,6))
            plt.plot(df['Step'], df['PotEng'], label="Potential Energy", color="red", linewidth=2)
            plt.plot(df['Step'], df['TotEng'], label="Total Energy",    color="blue", linewidth=2)
            for bp in breakpoints:
                plt.axvline(x=bp, color='grey', linestyle='dashdot', linewidth=1)
            plt.xlim(df['Step'].min(), df['Step'].max())
            plt.legend()
            plt.savefig(f"fig-step-Energy-Evolution-{os.path.splitext(file)[0]}.pdf", dpi=1200,transparent=True)
            plt.close()

            # Plot in terms of picoseconds
            plot_in_ps(df, os.path.splitext(file)[0])

        except Exception as e:
            print(f"Error processing {file}: {e}")


def combine_and_plot_all_logs(file_list):
    df_list = []
    cumulative_offset = 0
    for file in file_list:
        try:
            df = read_log_file(file)
            if 'v_simTime' not in df.columns:
                print(f"File {file} does not contain 'v_simTime' column. Skipping.")
                continue
            df['Step'] += cumulative_offset
            cumulative_offset = df['Step'].max()
            df_list.append(df)
        except Exception as e:
            print(f"Error processing {file}: {e}")

    if df_list:
        df_all = pd.concat(df_list, ignore_index=True)
        combined_csv = "data-combined_data.csv"
        df_all.to_csv(combined_csv, index=False)
        print(f"Combined log data saved to {combined_csv}")

        # Plotting combined data
        fig, ax1 = plt.subplots(figsize=(8,6))
        ax1.plot(df_all['Step'], df_all['c_sys'],   color='green',     label='Whole  System Temp', linewidth=3)
        ax1.plot(df_all['Step'], df_all['c_ex'],    color='blue',      label='External Only Temp', linewidth=3)
        ax1.plot(df_all['Step'], df_all['c_in'],    color='red',       label='Internal Only Temp', linewidth=3)
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Temp')
        ax1.set_xlim(df_all['Step'].min(), df_all['Step'].max())
        ax1.legend()
        ax1.tick_params(**tick_params)
        plt.tight_layout()
        plt.savefig("fig-combined_Temperature-Evolution.pdf", dpi=1200,transparent=True)
        plt.close()

        plt.figure(figsize=(8,6))
        plt.plot(df_all['Step'], df_all['PotEng'], label="Potential Energy", color="red", linewidth=2)
        plt.plot(df_all['Step'], df_all['TotEng'], label="Total Energy",    color="blue", linewidth=2)
        plt.xlim(df_all['Step'].min(), df_all['Step'].max())
        plt.legend()
        plt.savefig("fig-combined_Energy-Evolution.pdf", dpi=1200,transparent=True)
        plt.close()

        # Plot combined data in terms of picoseconds
        if 'Dt' in df_all.columns:
            df_all['Time_ps'] = df_all['Step'] * df_all['Dt']

            fig, ax1 = plt.subplots(figsize=(8,6))
            ax1.plot(df_all['Time_ps'], df_all['c_sys'],    color='green',    label='Whole  System Temp', linewidth=3)
            ax1.plot(df_all['Time_ps'], df_all['c_ex'],    color='blue',      label='External Only Temp', linewidth=3)
            ax1.plot(df_all['Time_ps'], df_all['c_in'],    color='red',       label='Internal Only Temp', linewidth=3)
            ax1.set_xlabel('Time (ps)')
            ax1.set_ylabel('Temp')
            ax1.set_xlim(df_all['Time_ps'].min(), df_all['Time_ps'].max())
            ax1.legend()
            ax1.tick_params(**tick_params)
            plt.tight_layout()
            plt.savefig("fig-ps-combined_Temperature-Evolution.pdf", dpi=1200,transparent=True)
            plt.close()

            plt.figure(figsize=(8,6))
            plt.plot(df_all['Time_ps'], df_all['PotEng'], label="Potential Energy", color="red", linewidth=2)
            plt.plot(df_all['Time_ps'], df_all['TotEng'], label="Total Energy",    color="blue", linewidth=2)
            plt.xlim(df_all['Time_ps'].min(), df_all['Time_ps'].max())
            plt.legend()
            plt.savefig("fig-ps-combined_Energy-Evolution.pdf", dpi=1200,transparent=True)
            plt.close()


def plot_in_ps(df, filename_prefix):
    # Assuming 'Dt' is a column in the DataFrame representing the timestep in ps
    if 'Dt' in df.columns:
        df['Time_ps'] = df['Step'] * df['Dt']

        # Plotting in terms of picoseconds
        fig, ax1 = plt.subplots(figsize=(8,6))
        ax1.plot(df['Time_ps'], df['c_sys'],    color='green',    label='Whole  System Temp', linewidth=3)
        ax1.plot(df['Time_ps'], df['c_ex'],    color='blue',      label='External Only Temp', linewidth=3)
        ax1.plot(df['Time_ps'], df['c_in'],    color='red',       label='Internal Only Temp', linewidth=3)
        ax1.set_xlabel('Time (ps)')
        ax1.set_ylabel('Temp')
        ax1.set_xlim(df['Time_ps'].min(), df['Time_ps'].max())
        ax1.legend()
        ax1.tick_params(**tick_params)
        plt.tight_layout()
        plt.savefig(f"fig-ps-Temperature-Evolution-{filename_prefix}.pdf", dpi=1200,transparent=True)
        plt.close()

        plt.figure(figsize=(8,6))
        plt.plot(df['Time_ps'], df['PotEng'], label="Potential Energy", color="red", linewidth=2)
        plt.plot(df['Time_ps'], df['TotEng'], label="Total Energy",    color="blue", linewidth=2)
        plt.xlim(df['Time_ps'].min(), df['Time_ps'].max())
        plt.legend()
        plt.savefig(f"fig-ps-Energy-Evolution-{filename_prefix}.pdf", dpi=1200,transparent=True)
        plt.close()


def main():
    log_files = ['log-1.txt', 'log-2.txt', 'log-3.txt', 'log-4.txt']
    process_and_plot_individual_logs(log_files)
    combine_and_plot_all_logs(log_files)


if __name__ == "__main__":
    main() 