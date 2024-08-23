sudo apt-get -y update
sudo apt-get -y install postgresql postgresql-server-dev-all python3.10-venv cmake build-essential
sudo service postgresql start
sudo -i -u postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'postgres'"
sudo -i -u postgres psql -U postgres -c 'DROP DATABASE IF EXISTS ourdb'
sudo -i -u postgres psql -U postgres -c 'CREATE DATABASE ourdb'

if [ -d ~/projects/lantern ]; then
  cd ~/projects && git clone --recursive https://github.com/lanterndata/lantern.git
  mkdir ~/projects/lantern/build
  cd ~/projects/lantern/build && cmake ..
  cd ~/projects/lantern/build && make install
fi

sudo -i -u postgres psql -U postgres -c 'CREATE EXTENSION lantern'

if [ -d ./movie_recommender ]; then
  wget -P movie_recommender https://paddlerec.bj.bcebos.com/aistudio/movies.dat --no-check-certificate
  wget -P movie_recommender https://paddlerec.bj.bcebos.com/aistudio/movie_vectors.txt --no-check-certificate
fi
