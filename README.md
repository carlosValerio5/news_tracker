# news_tracker

### Overview
The project offers a solution for UK students who are studying in a PR direction. The students need to track the most relevant news and make a presentation based on the most important news. To automate the process of “trend tracking” the university wants to implement a tool that collects the top daily news in the United Kingdom.<br>
The students will monitor how the biggest UK television BBC is holding the TOP of searches in the web. 


### Requirements
- Students must receive only verified information from BBC News and Google Trends.
- The solution must get all news from all BBC sections at least 3 times a day.
- Each new story's popularity must be estimated with Google Trends.
- Google Trends' current trends must be stored separately for each day.
- Headlines of BBC's main page must be stored separately as their "trend".
- Every day, the solution must send an email with 3 lists for the previous day (between 00:00 and 01:00 am): 1. Google trends; 2. BBC trends; 3. BBC all news ordered by trend score (max 50).
- The email should contain the percentage of matches between Google and BBC trends.
- A Web UI is required only for Administration purposes: changing the target email, number of news items, and the email sending period.


### Solution
The proposed system will aggregate news articles from the BBC and estimate their popularity using data from Google Trends.<br>
Users will receive a consolidated list featuring:
- News headlines from the BBC main page,
- Current trending topics from Google Trends,
- The top 50 BBC news articles ranked according to their estimated popularity as determined by Google Trends data.<br>

This solution aims to provide timely and relevant insights by combining authoritative news sources with dynamic trend analysis.

### Structure
database: All modules related to data base.<br>
aws_handler: Business logic for AWS.<br>
api: Modules related to api and its logic.<br>
helpers: unviersal directory for reusable methods.<br>

### Work Flow
<img width="975" height="486" alt="image" src="https://github.com/user-attachments/assets/3b7a2590-b1aa-4447-9a85-a123b59bc924" />

### Architecture
<img width="975" height="821" alt="image" src="https://github.com/user-attachments/assets/4b6e6fff-95eb-4e29-a181-1bc9ae34ebad" />

