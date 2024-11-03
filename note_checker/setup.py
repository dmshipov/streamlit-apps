from setuptools import setup, find_packages

setup(
    name='my_streamlit_app',  # Замени 'my_streamlit_app' на имя своего приложения
    version='0.1.0',  # Версия приложения
    packages=find_packages(),  # Автоматически найдет все пакеты в проекте
    install_requires=[
        'streamlit',  #  Streamlit,  конечно же
        'opencv-python',  #  Добавь эту строчку
        # ...  Добавь сюда все другие зависимости из  requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'my_app = my_streamlit_app.__main__:main',  #  Замени  'my_app' на то, что ты хочешь ввести в консоли, чтобы запустить приложение
        ],
    },
)
