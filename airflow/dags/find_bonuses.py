from email.mime.text import MIMEText
import os
import smtplib
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.models import TaskInstance
from datetime import datetime, timedelta
from utils.generic_scraper import findSUB
from utils.amex_scraper import amexScraper

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'compare_card_bonuses',
    default_args=default_args,
    description='Compare current card bonuses in Postgres with the newly scraped values',
    schedule_interval=timedelta(days=1),
    catchup=False
)

POSTGRES_CONN_ID = "postgres"

def send_email_basic(card, receivers):
    port = 465
    smtp_server = "smtp.gmail.com"
    sender = "campbellwang.dev@gmail.com"
    password = "" # can set this as env var

    email_message = f"""
    Hello!
    
    You are receiving this email because you signed up for updates on the {card['card_name']}.

    Here is the latest sign-up bonus we found: {card['new_bonus']}
    """

    message = MIMEText(email_message)
    message["Subject"] = "Your card's sign-up bonus has changed!"
    message["From"] = sender
    message["To"] = sender

    smtp_server = smtplib.SMTP_SSL(smtp_server, port)
    smtp_server.login(sender, password)
    smtp_server.sendmail(message["From"], receivers, message.as_string())
    smtp_server.quit()


def notification_task(updated_cards):
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    if updated_cards:
        for card in updated_cards:
            card_id = card['card_id']

            query = f"select email from tracker_subscription inner join tracker_subscriber on tracker_subscription.subscriber_id = tracker_subscriber.id where tracker_subscription.card_id = {card_id};"

            cursor.execute(query)
            emails = cursor.fetchall()

            send_email_basic(card, [email[0] for email in emails])

def compare_card_bonuses(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT "id", "name", "type", "currentBonus", "link"
        FROM "tracker_card";
    """)
    cards = cursor.fetchall()

    updated_cards = []

    for card in cards:
        id, name, type, current_bonus, link = card

        if type == 'AMEX':
            scraped_bonus = amexScraper(link)
        else:
            scraped_bonus = findSUB(link)
        
        if scraped_bonus != current_bonus:
            updated_cards.append({'card_id': id, 'card_name': name, 'new_bonus': scraped_bonus})
            cursor.execute(f"""UPDATE tracker_card SET "currentBonus" = {scraped_bonus} WHERE name = '{name}';""")
            conn.commit()
    
    cursor.close()
    conn.close()
    notification_task(updated_cards)

t1 = PythonOperator(
    task_id='compare_card_bonuses',
    python_callable=compare_card_bonuses,
    dag=dag,
)