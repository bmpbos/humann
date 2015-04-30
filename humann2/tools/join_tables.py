#!/usr/bin/env python

"""
Join a set of gene, pathway, or taxonomy tables into a single table

This module will join gene and pathway tables output by HUMAnN2. 

Dependencies: Biom (only required if running with .biom files)

To Run: 
$ ./join_tables.py -i <input_dir> -o <gene_table.{tsv,biom}>

"""

import argparse
import sys
import tempfile
import os
import shutil
import re

import util

GENE_TABLE_DELIMITER="\t"
BIOM_FILE_EXTENSION=".biom"
TSV_FILE_EXTENSION=".tsv"
        
def join_gene_tables(gene_tables,output,verbose):
    """
    Join the gene tables to a single gene table
    """
    
    gene_table_data={}
    start_column_id=""
    samples=[]
    for index,gene_table in enumerate(gene_tables):
        
        if verbose:
            print("Reading file: " + gene_table)
        
        file_handle,header,line=util.process_gene_table_header(gene_table, allow_for_missing_header=True)
        
        if header:
            header_info=header.rstrip().split(GENE_TABLE_DELIMITER)
            if not start_column_id:
                start_column_id=header_info[0]
            sample_name=header_info[1]
        else:
            # if there is no header in the file then use the file name as the sample name
            sample_name=os.path.splitext(os.path.basename(gene_table))[0]
        
        samples.append(sample_name)
        while line:
            data=line.rstrip().split(GENE_TABLE_DELIMITER)
            try:
                gene=data[0]
                data_point=data[1]
            except IndexError:
                gene=""

            if gene:
                current_data=gene_table_data.get(gene,"")
                fill = index - current_data.count(GENE_TABLE_DELIMITER)
                if fill > 0:
                    # fill in zeros for samples without data then add data point
                    gene_table_data[gene]=current_data + GENE_TABLE_DELIMITER.join(["0"]*fill) + GENE_TABLE_DELIMITER + data_point + GENE_TABLE_DELIMITER
                elif fill < 0:
                    # add data point to other data point from the same sample
                    current_data_points=current_data.split(GENE_TABLE_DELIMITER)
                    current_data_points[-2]=str(float(current_data_points[-2])+float(data_point))
                    gene_table_data[gene] = GENE_TABLE_DELIMITER.join(current_data_points)
                else:
                    # add data point to end of list
                    gene_table_data[gene] = current_data + data_point + GENE_TABLE_DELIMITER

            line=file_handle.readline()
            
        file_handle.close()
                
    # write the joined gene table
    if not start_column_id:
        start_column_id="# header "
    sample_header=[start_column_id]+samples
    total_gene_tables=len(samples)
    sorted_gene_list=sorted(list(gene_table_data))
    try:
        file_handle=open(output,"w")
        file_handle.write(GENE_TABLE_DELIMITER.join(sample_header)+"\n")
    except EnvironmentError:
        sys.exit("Unable to write file: " + file)  
        
    for gene in sorted_gene_list:
        # extend gene data for any gene that is not included in all samples
        current_data=gene_table_data[gene]
        fill = total_gene_tables - current_data.count(GENE_TABLE_DELIMITER)
        if fill:
            current_data=current_data + GENE_TABLE_DELIMITER.join(["0"]*fill) + GENE_TABLE_DELIMITER
        file_handle.write(gene+GENE_TABLE_DELIMITER+current_data.rstrip(GENE_TABLE_DELIMITER)+"\n")
    
    file_handle.close()

def parse_arguments(args):
    """ 
    Parse the arguments from the user
    """
    
    parser = argparse.ArgumentParser(
        description= "Join gene, pathway, or taxonomy tables\n",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-v","--verbose", 
        help="additional output is printed\n", 
        action="store_true",
        default=False)
    parser.add_argument(
        "-i","--input",
        help="the directory of tables\n",
        required=True)
    parser.add_argument(
        "-o","--output",
        help="the table to write\n",
        required=True)
    parser.add_argument(
        "--file_name",
        help="only join tables with this string included in the file name")

    return parser.parse_args()


def main():
    # Parse arguments from command line
    args=parse_arguments(sys.argv)
    
    # check for format of the gene tables
    input_dir=os.path.abspath(args.input)
    
    # check the directory exists
    if not os.path.isdir(input_dir):
        sys.exit("The input directory provided can not be found." + 
            "  Please enter a new directory.")
    
    
    gene_tables=[]
    file_list=os.listdir(input_dir)
    
    # filter out files which do not meet the name requirement if set
    biom_flag=False
    if args.file_name:
        reduced_file_list=[]
        for file in file_list:
            if re.search(args.file_name,file):
                reduced_file_list.append(file)
                if file.endswith(BIOM_FILE_EXTENSION):
                    biom_flag=True
        file_list=reduced_file_list
    else: 
        for file in file_list:
            if file.endswith(BIOM_FILE_EXTENSION):
                biom_flag=True
            
    # Check for the biom software if running with a biom input file
    if biom_flag:
        if not util.find_exe_in_path("biom"):
            sys.exit("Could not find the location of the biom software."+
            " This software is required since the input file is a biom file.")       
    
    args.output=os.path.abspath(args.output)
    output_dir=os.path.dirname(args.output)
    
    # Create a temp folder for the biom conversions
    if biom_flag:
        temp_dir=tempfile.mkdtemp( 
            prefix='humann2_split_gene_tables_', dir=output_dir)
        if args.verbose:
            print("Temp folder created: " + temp_dir)
    
    for file in file_list:
        if file.endswith(BIOM_FILE_EXTENSION):
            # create a new temp file
            file_out, new_file=tempfile.mkstemp(dir=temp_dir)
            os.close(file_out)
        
            # convert biom file to tsv
            if args.verbose:
                print("Processing file: " + os.path.join(input_dir,file))
            util.biom_to_tsv(os.path.join(input_dir,file),new_file)
            gene_tables.append(new_file)
        else:
            gene_tables.append(os.path.join(input_dir,file))
        
    # split the gene table
    if args.verbose:
        print("Joining gene table")
        
    if biom_flag:
        # create a new temp file
        file_out, new_file=tempfile.mkstemp(dir=temp_dir)
        os.close(file_out)
        join_gene_tables(gene_tables,new_file,args.verbose)
        util.tsv_to_biom(new_file, args.output)
    else:
        join_gene_tables(gene_tables,args.output,args.verbose)
            
    # deleting temp folder with all files
    if biom_flag:
        if args.verbose:
            print("Deleting temp files in temp folder: " + temp_dir)
        shutil.rmtree(temp_dir)
    
    print("Gene table created: " + args.output)

if __name__ == "__main__":
    main()
