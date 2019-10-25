##              To Do List
##              1. clean up the directories by making them dynamic
##              2. get the new file out of the attachment combiner function
##              3. get the file into the file mailer function
##              4. need to retrieve the opportunity ID from salesforce\
##              5. need to combine the opportunity id with our combined results lists before they are mailed to the OPS team

############to make this work
#1. Set the email subject on line 37
#2. Set the sheet names in the POA lists to their equivelant sheet in the Eloqua results
#3. Update the POA_Eloqua_email_and_lists.xlsx dataframe with the corfrelating POA lists and Eloqua Results names
#4. Set the eloqua_results_file_locations for the correct month
#5. Set the POA_lists_file_location for the correct month

#this library is to set the directory
import os

#these libraries are to manipulate the excel files
import pandas as pd
import openpyxl
import csv

#this library is to interact with MS Outlook
import win32com.client as win32

#this library is to check todays date
import datetime


##The below code helps by downloading the attachments from outlook emails that are 'Unread' (and changes the mail to Read.) or from 'Today's' date.without altering the file name. Just pass the 'Subject' argument.
##https://stackoverflow.com/questions/39656433/how-to-download-outlook-attachment-from-python-script
eloqua_results_file_locations = r'C:\Users\isaama2\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.7\Test Programs\Test Attachments\Email List Results Sent to POA Team\September'
email_subject = 'FW: September'
def saveattachments(email_subject, eloqua_results_file_locations):
    path = eloqua_results_file_locations
    #print(path)
    today = datetime.date.today()
    outlook = win32.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6) 
    messages = inbox.Items
    #set the title of the email you want to look for here. can we use regex to make flexible email title searches?
    for message in messages:
        if message.Subject == email_subject: #and message.Unread or message.Senton.date() == today:
            #body_content = message.body
            attachments = message.Attachments
            attachment = attachments.Item(1)
            for attachment in message.Attachments:
                attachment.SaveAsFile(os.path.join(path, str(attachment)))
                #if message.Subject == subject and message.Unread:
                #    message.Unread = False
                print('Attachment Saved!')

##saveattachments(email_subject, eloqua_results_file_locations)


###~##create a dictionary using the reference sheet. references the dictionary to to know which file sent from the POA team to the eloqua team to use as a resource to retrieve TaxID. Then saves the combined sheet
POA_Eloqua_Team_Dataframe_Location = r'C:\Users\isaama2\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.7\Test Programs\Test Attachments'
def dictionary_creater(POA_Eloqua_Team_Dataframe_Location):
    os.chdir(POA_Eloqua_Team_Dataframe_Location)
    #get the read excel to just open the dataframe name
    df = pd.read_excel('POA_Eloqua_email_and_lists.xlsx')
    eloqua_results_dictionary = df.set_index('POA File Name')['Eloqua File Name'].to_dict()
    print('Dictionary made')
    return(eloqua_results_dictionary)
    
eloqua_results_dictionary = dictionary_creater(POA_Eloqua_Team_Dataframe_Location)


###~~~this code checks if we successfully created the dictionary to correlate eloqua results files with POA lists
for key, val in eloqua_results_dictionary.items():
    print(key, "=>", val)
    

###function to find a filename and its corresponding key, then combine the file and its key
combined_results_file_location = r'C:\Users\isaama2\Desktop\Eloqua Data Combiner Files\Test File Combiner Folder'
POA_lists_file_location = r'C:\Users\isaama2\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Python 3.7\Test Programs\Test Attachments\Email Lists Sent to Eloqua Team\September Files'
def attachment_combiner(eloqua_results_dictionary, eloqua_results_file_locations, POA_lists_file_location, combined_results_file_location):
    files = os.listdir(POA_lists_file_location)
    for POA_file in files:
        print(POA_file)
        os.chdir(POA_lists_file_location)
        sheets = pd.ExcelFile(POA_file)
        sheets = sheets.sheet_names
        print(sheets)
        for POA_sheet in sheets:
            Eloqua_file = eloqua_results_dictionary[POA_file]
            os.chdir(POA_lists_file_location)
            #print(Eloqua_file)
            secondary = pd.read_excel(POA_file, sheet_name = POA_sheet, index_col = None)
            os.chdir(eloqua_results_file_locations)
            main = pd.read_excel(Eloqua_file, sheet_name = POA_sheet, index_col = None)
            combined = pd.merge(main, secondary, sort=False, left_on=['Email Address'], right_on=['Contact: Primary Contact Email'], how = 'left') #define what you are combining on, and then make sure you are combining into file containing Eloqua results
            os.chdir(combined_results_file_location)
            file_name = POA_file + ' + ' + POA_sheet + ' done by Python.xlsx'
            combined.to_excel(file_name, index=False)
            print('Eloqua combination complete! file saved to folder!')

attachment_combiner(eloqua_results_dictionary, eloqua_results_file_locations, POA_lists_file_location, combined_results_file_location)


#function to combine the results sheet, with the opportunity ID list, so they can be uploaded to salesforce
opportunity_ID_file_location = r'C:\Users\isaama2\Desktop\Eloqua Data Combiner Files\Opportunity ID Reference Folder\Opportunity ID Reference File.xlsx' 
new_combined_file_with_opportunity_ID_directory = r'C:\Users\isaama2\Desktop\Eloqua Data Combiner Files\Test File Combiner Folder\Test Files With Opportunity ID'
def opportunity_ID_combiner(opportunity_ID_file_location, combined_results_file_location, new_combined_file_with_opportunity_ID_directory):
    files = os.listdir(combined_results_file_location)
    for combined_file in files:
                os.chdir(combined_results_file_location)
                combined_results_file = pd.read_excel(combined_file, index_col = None)
                opportunity_ID_file = pd.read_excel(opportunity_ID_file_location, index_col = None)  #it is set up for .xlsx
                combined = pd.merge(combined_results_file, opportunity_ID_file, on = 'Tax ID', how = 'outer')  
                file_name = combined_file
                os.chdir(new_combined_file_with_opportunity_ID_directory)
                combined.to_excel(file_name, index = False)
                print('Opportunity ID Combination for ' + combined_file + 'complete!')

opportunity_ID_combiner(opportunity_ID_file_location, combined_results_file_location, new_combined_file_with_opportunity_ID_directory)


#function to send each file that has been combined with Opportunity ID and in an Outlook email
def mail_the_files_to_ops(new_combined_file_with_opportunity_ID_directory):
        outlook = win32.Dispatch('outlook.application')
        files = os.listdir(new_combined_file_with_opportunity_ID_directory)
        for file in files:
            mail = outlook.CreateItem(0)    
            mail.To = 'isaama2@vsp.com'
            mail.Subject = 'Perfect Pair Rebate List'
            mail.Body = 'Hi Alex, \r\n\nHere is the perfect pair rebate list!\r\n\nCheers, \r\nIsaac'
            attachment = r'\\ntsca126\PRmisc\Provider Operations and Analysis\Reporting & Analytics\Marketing\Sales\POA-1364 Perfect Pair Rebate\POA-1164 Development\python perfect pair.xlsx'
            #attachment = directory + '\\' + file_name #will this work? putting the slash infront of this?
            print('working correctly')
            mail.Attachments.Add(attachment)
            mail.Send()
            #clarify it worked
        print('Operation successful!')

##mail_the_files_to_ops(new_combined_file_with_opportunity_ID_directory)
