import unittest
import logging
import tempfile
import math

import cfg
import utils

from humann2.search import nucleotide
from humann2 import store
from humann2 import config
from humann2 import utilities

class TestAdvancedHumann2NucleotideSearchFunctions(unittest.TestCase):
    """
    Test the functions found in humann2.search.nucleotide
    """
    
    def setUp(self):
        config.unnamed_temp_dir=tempfile.gettempdir()
        config.temp_dir=tempfile.gettempdir()
        config.file_basename="HUMAnN2_test"
        
        # set up nullhandler for logger
        logging.getLogger('humann2.search.nucleotide').addHandler(logging.NullHandler())

    def test_nucleotide_search_unaligned_reads_output_fasta_format(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test output file is of fasta format
        Test sam file is not removed
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # check for fasta output file format
        file_format=utilities.determine_file_format(unaligned_reads_file_fasta)
        self.assertEqual("fasta",file_format)
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)


    def test_nucleotide_search_unaligned_reads_read_count_aligned(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test for aligned read counts
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # check the aligned reads count
        self.assertEqual(len(alignments.get_hit_list()),cfg.sam_file_unaligned_reads_total_aligned)
        
    def test_nucleotide_search_unaligned_reads_read_count_aligned_evalue_threshold(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test for aligned read counts
        Test the evalue threshold does not filter alignments
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # update the evalue threshold to a number less than those for the alignment file
        original_evalue_threshold=config.evalue_threshold
        config.evalue_threshold=1e-15
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # reset the evalue threshold back to the original
        config.evalue_threshold=original_evalue_threshold
        
        # check the aligned reads count (all reads should be aligned even though they do not
        # meet the threshold as the evalue threshold is not applied for this type of alignment)
        self.assertEqual(len(alignments.get_hit_list()),cfg.sam_file_unaligned_reads_total_aligned)
        
    def test_nucleotide_search_unaligned_reads_read_count_aligned_identity_threshold(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test for aligned read counts
        Test the identity threshold does filter alignments
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # update the identity threshold to a number larger than those in the alignments
        original_identity_threshold=config.identity_threshold
        config.identity_threshold=101.0
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # reset the identity threshold back to the original
        config.identity_threshold=original_identity_threshold
        
        # check the aligned reads count (it should be zero as none should pass the threshold)
        self.assertEqual(len(alignments.get_hit_list()),0)

    def test_nucleotide_search_unaligned_reads_read_count_unaligned(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test for unaligned read counts
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # check the unaligned reads count
        self.assertEqual(unaligned_reads_store.count_reads(),cfg.sam_file_unaligned_reads_total_unaligned)
        
    def test_nucleotide_search_unaligned_reads_read_count_unaligned_minimize_memory_use(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test for unaligned read counts
        Test with minimize memory use
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads(minimize_memory_use=True)
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_unaligned_reads, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # check the unaligned reads count
        self.assertEqual(unaligned_reads_store.count_reads(),cfg.sam_file_unaligned_reads_total_unaligned)
        
    def test_nucleotide_search_unaligned_reads_annotations_reference(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test the different annotation formats are recognized for reference
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_annotations, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # two of the hits should be for gene "UniRef50"
        hits=alignments.hits_for_gene("UniRef50")
        self.assertEqual(len(hits),2)
        
                
    def test_nucleotide_search_unaligned_reads_annotations_bug(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test the different annotation formats are recognized for bug
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_annotations, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # there should be one bug which is unclassified
        self.assertEqual(alignments.bug_list(),["unclassified"])
        
    def test_nucleotide_search_unaligned_reads_annotations_gene_length(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test the different annotation formats are recognized for gene length
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_annotations, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # there should be 4 hits identified
        all_hits=alignments.get_hit_list()
        self.assertEqual(len(all_hits),4)
        
        # check for set and default gene lengths
        for hit in all_hits:
            query, bug, reference, score, length = hit
            if reference == "UniRef50":
                self.assertEqual(length,2000/1000.0)
            else:
                self.assertEqual(length,1000/1000.0)
                
    def test_nucleotide_search_unaligned_reads_scores(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test the scores are based on percent identities
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_annotations, alignments, unaligned_reads_store, keep_sam=True) 
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)
        
        # there should be 4 hits identified
        all_hits=alignments.get_hit_list()
        
        # check for set and default gene lengths
        expected_score=math.pow(100.0, config.identity_power)
        
        for hit in all_hits:
            query, bug, reference, score, length = hit
            self.assertEqual(score,expected_score)

    def test_nucleotide_search_unaligned_reads_output_blast_format(self):
        """
        Test the unaligned reads and the store alignments
        Test with a bowtie2/sam output file
        Test the aligned reads file created is of the blastm8 format
        """
        
        # create a set of alignments
        alignments=store.Alignments()
        unaligned_reads_store=store.Reads()
        
        config.file_basename="TEST"
        
        # read in the aligned and unaligned reads
        [unaligned_reads_file_fasta, reduced_aligned_reads_file] = nucleotide.unaligned_reads(
            cfg.sam_file_annotations, alignments, unaligned_reads_store, keep_sam=True) 
        
        # test file is of the blastm8 format
        file_format=utilities.determine_file_format(reduced_aligned_reads_file)
        
        # remove temp files
        utils.remove_temp_file(unaligned_reads_file_fasta)
        utils.remove_temp_file(reduced_aligned_reads_file)           
        
        self.assertEqual(file_format,"blastm8")
        
        
        
        
        


