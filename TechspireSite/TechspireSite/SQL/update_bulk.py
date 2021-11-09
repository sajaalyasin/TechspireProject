import glob
import os


def alter_bulk_insert():
    original = open("BulkInsert.sql", "r")
    modified = open("BulkInsertC.sql", "w")
    org_data = original.read()
    mod_data = org_data.replace("D:", "C:")
    mod_data = mod_data.replace("\\n", "0x0a")
    modified.write(mod_data)
    modified.close()
    original.close()

if __name__ == '__main__':
    alter_bulk_insert()

