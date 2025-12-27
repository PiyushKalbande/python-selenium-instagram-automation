# 📸 Instagram Story Viewer Automation

Maine ye project Instagram stories ko automate karne ke liye banaya hai. Is script ka main kaam hai bina manually click kiye stories ko automatic view karna, aur ye itna smart hai ki ye Image aur Video stories ke beech ka farak samajh leta hai.

## 🤖 Isme Khaas Kya Hai? (Features)

*   **Human-Like Behavior:** Ye `undetected-chromedriver` use karta hai taaki Instagram ko shak na ho ki koi bot chal raha hai.
*   **Smart Detection:** 
    *   Image story dikhne par 5 seconds rukta hai.
    *   Video story dikhne par 10 seconds rukta hai.
*   **Manual Intervention:** Agar aap script chalte waqt khud se `Arrow Key` dabate ho ya `Mouse Click` karte ho, toh script itni smart hai ki wo samajh jayegi aapne skip kiya hai.
*   **Security Friendly:** Agar login ke time Captcha ya OTP maangta hai, toh script wahi ruk jayegi aur aapke manual entry ka wait karegi.
*   **Logging:** Saara record `instagram_automation.log` file mein save hota hai.

## 🛠️ Setup Kaise Karein?

1.  **Clone the Repo:**
    ```bash
    git clone github.com
    cd python-selenium-instagram-automation
    ```

2.  **Dependencies Install Karein:**
    ```bash
    pip install undetected-chromedriver selenium python-dotenv
    ```

3.  **Environment Setup:**
    Ek `.env` file banayein aur usme apni login details daalein:
    ```text
    INSTA_USERNAME=aapka_username
    INSTA_PASSWORD=aapka_password
    ```
