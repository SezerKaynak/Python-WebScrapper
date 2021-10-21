
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import matplotlib.pyplot as plt
import openpyxl
from kora.selenium import wd

wd.get('https://www.ensonhaber.com')
title_of_news = []
date_of_news = []
content_of_news = []
category_of_news = []
wd.execute_script("window.scrollTo(0, 300)")
size_of_slider = 20

# I'm taking news from slider. Every news in slider is opening in a new tab. Then program is taking source of page.
# After that, program is closing the tab. This process continues until all news in the slider is open. size_of_slider
# denotes the how many tabs to open. If ad open in new tab, program close the tab automatically.
i = 1
while i < size_of_slider:
    wd.find_element_by_xpath(f'/html/body/div[2]/div[4]/div[1]/div[2]/div[2]/div[{i}]/a/span').click()
    window_after = wd.window_handles[1]
    wd.switch_to.window(window_after)
    content = wd.page_source
    source = BeautifulSoup(content, 'html.parser')
    site_link = wd.current_url
    if 'https://www.ensonhaber.com/' in site_link:
        title_of_news.append(source.title.string.split())
        date_of_news.append(source.find("div", class_="c-date").findNext("li").next_sibling.next_sibling.text.split())
        category_of_news.append(
            source.find('div', class_='bread').findNext('li').next_sibling.next_sibling.text.split())
        content_of_news.append(source.find('div', class_='c-desc').text.split())
        window_after = wd.window_handles[0]
        wd.close()
        wd.switch_to.window(window_after)
    else:
        window_after = wd.window_handles[0]
        wd.close()
        wd.switch_to.window(window_after)
    i += 1
wd.close()

# I wrote this function to take frequencies of words.


def split_and_get_freq(sentences, number):
    words_of_sentences = []
    freq = []
    split_word_list = []
    if number == 3:
        for word in sentences:
            freq.append(sentences.count(word))
        return sentences, freq
    for i in sentences:
        words_of_sentences.append(i)
    for j in words_of_sentences:
        for word in j:
            freq.append(j.count(word))
    for k in words_of_sentences:
        for d in k:
            split_word_list.append(d)
    return split_word_list, freq

# I wrote this function to create an excel file and store the dataframe into it. If number is 3, it means dataframe for
# frequency of categories by date, program is checking whether the news received from internet are on same date. If the
# news received from internet have different date, program is creating a new array called different_day and news with
# different dates are storing in it. After that, program is creating dataframes for every single array and for every
# dataframes, program is creating excel files. This program only works if date of news are two different dates. Because
# ensonhaber.com always updating its news and news never has three different dates.


def create_excel(data, number):
    same_day = []
    different_day = []
    if number == 3:
        temp = edit_categories_and_dates(category_of_news, date_of_news)[2][0]
        date_list = edit_categories_and_dates(category_of_news, date_of_news)[2]
        i = 0
        while i < len(date_list):
            if date_list[i] != temp:
                different_day.append(data[i])
            else:
                same_day.append(data[i])
            i += 1
        df = pd.DataFrame({
            'freq': split_and_get_freq(same_day, number)[1],
            'split': split_and_get_freq(same_day, number)[0],
        })
        df.to_excel(f'data{number}.xlsx', index=False)
        if len(different_day) != 0:
            df = pd.DataFrame({
                'freq': split_and_get_freq(different_day, number)[1],
                'split': split_and_get_freq(different_day, number)[0],
            })
            df.to_excel(f'data{number + 1}.xlsx', index=False)
    else:
        df = pd.DataFrame({
            'freq': split_and_get_freq(data, number)[1],
            'split': split_and_get_freq(data, number)[0],
        })
        df.to_excel(f'data{number}.xlsx', index=False)

# I wrote this function to edit categories and split date to only day.


def edit_categories_and_dates(sentences, dates):
    edited_sentences = []
    for j in sentences:
        new = ''
        for k in j:
            new = new + k + ' '
        edited_sentences.append(new)
    date = []
    for i in dates:
        date.append(i[0])
    split_date = []
    for j in date:
        split_date.append(j.split("."))
    only_day = []
    k = 0
    while k < len(split_date):
        only_day.append(split_date[k][0])
        k += 1
    return edited_sentences, date, only_day

# In this function program is creating graphs with data from excel files. If number is 3 and if news have different
# dates, program is creating 2 different graphs for 2 different date.


def draw_graph(number):
    if number == 1:
        x_size = 30
        y_size = 8
        text = 'Frequency of Words in All Titles'
        rotation = 90
    elif number == 2:
        x_size = 40
        y_size = 8
        text = 'Frequency of Words in All Scraping Text'
        rotation = 90
    else:
        x_size = 8
        y_size = 5
        text = ''
        rotation = 0
    temp = edit_categories_and_dates(category_of_news, date_of_news)[2][0]
    date_list = edit_categories_and_dates(category_of_news, date_of_news)[2]
    if number == 3:
        i = 0
        data = pd.read_excel(f'data{number}.xlsx')
        plt.figure(figsize=(x_size, y_size))
        plt.bar(data.split, data.freq)
        plt.title(f'Frequency of Categories by Date: {edit_categories_and_dates(category_of_news, date_of_news)[1][0]}')
        plt.tick_params(axis='x', which='major', labelsize=7, rotation=rotation)
        plt.tight_layout()
        plt.show()
        while i < len(date_list):
            if date_list[i] != temp:
                data = pd.read_excel(f'data{number + 1}.xlsx')
                plt.figure(figsize=(x_size, y_size))
                plt.bar(data.split, data.freq)
                plt.title(
                    f'Frequency of Categories by Date:{edit_categories_and_dates(category_of_news, date_of_news)[1][i]}')
                plt.tick_params(axis='x', which='major', labelsize=7, rotation=rotation)
                plt.tight_layout()
                plt.show()
                break
            i += 1
    else:
        data = pd.read_excel(f'data{number}.xlsx')
        plt.figure(figsize=(x_size, y_size))
        plt.bar(data.split, data.freq)
        plt.title(text)
        plt.tick_params(axis='x', which='major', labelsize=7, rotation=rotation)
        plt.tight_layout()
        plt.show()


create_excel(title_of_news, 1)
draw_graph(1)
create_excel(content_of_news, 2)
draw_graph(2)
create_excel(edit_categories_and_dates(category_of_news, date_of_news)[0], 3)
draw_graph(3)
