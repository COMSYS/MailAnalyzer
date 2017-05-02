# MailAnalyzer

Tool to assess the prevalence of cloud computing in the email landscape based on inspecting headers of (received) emails.

## About

This repository contains the aggregated measurements results of the [TMA 2017](http://tma.ifip.org/) paper [Veiled in Clouds? Assessing the Prevalence of Cloud Computing in the Email Landscape](https://www.comsys.rwth-aachen.de/fileadmin/papers/2017/2017-henze-tma-cloudemail.pdf) as well as the source code and instructions to reproduce these numbers. Furthermore, we provide the necessary scripts to directly analyze (your own) mailboxes for cloud usage.

If you use any portion of MailAnalyzer in your work, please cite the following paper:

Martin Henze, Mary Peyton Sanford and Oliver Hohlfeld
Veiled in Clouds? Assessing the Prevalence of Cloud Computing in the Email Landscape
Proceedings of the 2017 Network Traffic Measurement and Analysis Conference (TMA 2017), Dublin, Ireland 
June 2017.

BibTeX:
```
@inproceedings {mailanalyzer,
   author = {Henze, Martin and Sanford, Mary Peyton and Hohlfeld, Oliver},
   title = {{Veiled in Clouds? Assessing the Prevalence of Cloud Computing in the Email Landscape}},
   booktitle = {Proceedings of the 2017 Network Traffic Measurement and Analysis Conference (TMA 2017)},
   year = {2017},
}
```

## Dependencies

MailAnalyzer has been developed for Python 2.7 and requires the installation of the following packages (e.g., using `pip`):
* `py-radix`
* `pytz`

## Datasets

As described in the paper (see above), we used MailAnaylzer to study the prevalence of cloud computing in different email datasets. Our source code release includes scripts to retrieve the public datasets for mailing lists and WikiLeaks (see the paper for details).

* Mailing lists
   * Apache: `tools/apache_download.py`
   * Dovecot: `tools/dovecot_download.sh`
   * FreeBSD: `tools/freebsd_download.sh`
   * IETF: `tools/ietf_download.sh`
   * openSUSE: `tools/opensuse_download.py`
* WikiLeaks
   * AKP: `tools/wikileaks-akp_download.sh`
   * DNC: `tools/wikileaks-dnc_download.sh`
   * Podesta: `tools/wikileaks-podesta_download.sh`

## Usage

### Operating on datasets

We provide one dedicated script for each of the datasets:

* Mailing lists
   * Apache: `apache.py`
   * Dovecot: `dovecot.py`
   * FreeBSD: `freebsd.py`
   * IETF: `ietf.py`
   * openSUSE: `opensuse.py`
* WikiLeaks
   * AKP: `wikileaks-akp.py`
   * DNC: `wikileaks-dnc.py`
   * Podesta: `wikileaks-podesta.py`
   
After downloading the corresponding dataset, open the Python file and configure the input directory (`dir_name`) and output prefix (`output`). Directories specified in the output prefix must exist and be writable. After configuring input and output, simply execute the script to start the analysis. Depending on the dataset and your machine, this process can take up to several hours. All output will be written to the specified output path.

### Operating on mailboxes

We provide different scripts to directly operate on (your own) mailboxes:

* `applemail.py`: Operates on mailboxes in the format of Apple's Mail app
* `imap.py`: Operates on mailboxes via IMAP
* `maildir.py`: Operates on mailboxes in the Maildir format
* `thunderbird.py`: Operates on mailboxes in the format of Mozilla's Thunderbird

The individual scripts are configured and run similar to the scripts operating on datasets (see above). Additionally, these scripts provide the possibility to "blacklist" a certain cloud provider. This is useful if the mailbox is hosted by one of the 31 cloud providers under study (otherwise, the results would indicate a cloud usage of 100%). To this end, it is possible to define pattern strings matching filenames (using Python's `fnmatch`) for which a specified provider should be ignored. More documentation and a list of providers that can be blacklisted is provided in the individual scripts.

## Results

In case you do not want to obtain the datasets and re-run all measurements yourself, we provide the aggregated results as presented in the paper in the `results` directory. Due to legal reasons, we cannot provide the aggregated results for the users dataset.

Results consist of two CSV files per dataset. Here, `provider_data.csv` contains statistics on cloud usage in general, while `hidden_provider_data.csv` contains statistics on hidden cloud usage (see the paper for a precise definition of this term). Both files first provide (identical) statistics combined over all cloud providers (Total Mails, Total Detected, Hidden Partial, Hidden Full). Thereby, cloud usage is *partial* if at least one used cloud provider cannot be derived from sender and receiver addresses and *full* if none of the used cloud providers cannot be derived from sender and receiver addresses. The subsequent columns contain the number of emails that used a specific cloud service, in case of `hidden_provider_data.csv` only hidden usage is reported.

## Contributors

* Code: Martin Henze, Mary Peyton Sanford
* Detection patterns: Martin Henze, Erik Mühmer, Jan Pennekamp, Mary Peyton Sanford

MailAnalyzer has been developed at the [Chair of Communication and Distributed Systems](https://www.comsys.rwth-aachen.de/) at [RWTH Aachen University](https://www.rwth-aachen.de/). This work has received funding from the German Federal Ministry of Education and Research (BMBF) under project funding reference no. 16KIS0351 (TRINICS) and the European Union’s Horizon 2020 research and innovation program 2014-2018 under grant agreement no. 644866 (SSICLOPS).
