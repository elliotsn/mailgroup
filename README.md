  ******************
  *  mailgroup.py  *
  ******************

  SUMMARY

  Program to produce a string that can be pasted into a mail client. The
  string is a list of email addresses that is constructed from 2 linked csv
  files: a database of email addresses, and a database of group names.

  USAGE

  mailgroup EMAIL_LIST GROUP_LIST [GROUPS]

  EMAIL_LIST is the path to a csv file containing the database of email
          addresses. The file must contain the colums (with a header row):
                  'Last name', 'First name', 'Email', 'Groups'
          Additional columns may be present (e.g. Position, Notes) but will
          not be used.

  GROUP_LIST is the path to a csv file containing the database of email
          groups. The file must contain the columns (with a header row):
              'Group', 'Key'

  [GROUPS]   is a logical expression built using the logical operators & | ~
          and parentheses (), as well as group names that exist in
          the GROUP_LIST file.

  If no arguments or the wrong number of arguments are passed then this
  message is returned.

  When EMAIL_LIST and GROUP_LIST are defined a string is returned to stdout
  that summarizes the number of names and groups in the database.

  When [GROUPS] is defined the output returned to stdout is a list of email
  addresses of members belonging to the groups listed in [GROUPS].

  Example command and output:
      $  mailgroup members.csv groups.csv (project1&project2)|management
      $  John Doe <j.doe@theinter.net>, Jane Q. Doe <jane.doe@theother.net>,
      $  James Manager <jims.your@boss.com>

  Note that commas are removed from member names stored in EMAIL_LIST, because
  these are interpreted as field separators by most email clients and
  interfaces.

  Author: Elliot Sefton-Nash (e.sefton-nash@uclmail.net)
