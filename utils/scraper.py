from icrawler.builtin import BingImageCrawler
import os
import time

politicians = [
    "Imran Khan",
    "Nawaz Sharif",
    "Shehbaz Sharif",
    "Bilawal Bhutto",
    "Asif Ali Zardari",
    "Maryam Nawaz",
    "Fawad Chaudhry",
    "Shah Mahmood Qureshi",
    "Khawaja Asif",
    "Hamza Shehbaz",
    "Faisal Vawda",
    "Murad Ali Shah",
    "Siraj ul Haq",
    "Pervez Khattak",
    "Mahmood Khan Achakzai",
    "Ahmed Sharif Chaudhry"
]

BASE_DIR = "dataset/raw"

for politician in politicians:

    folder_name = politician.lower().replace(" ", "_")

    save_path = os.path.join(BASE_DIR, folder_name)

    os.makedirs(save_path, exist_ok=True)

    print(f"\nDownloading images for: {politician}")

    crawler = BingImageCrawler(
        downloader_threads=4,
        storage={'root_dir': save_path}
    )

    try:
        crawler.crawl(
            keyword=politician,
            max_num=120
        )

        print(f"Completed: {politician}")

    except Exception as e:
        print(f"Error for {politician}: {e}")

    time.sleep(2)

print("\nDataset collection completed.")