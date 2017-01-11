This is a markdown file explaining

Steps to install VIM
Lots of stuff from here
https://realpython.com/blog/python/vim-and-python-a-match-made-in-heaven/

$> sudo apt-get install vim-nox-py2
$> git clone dotfiles and link ~/.vimrc to ~/dotfiles/vimrc
$> vim

in VIM run :PluginInstall to install all plugins

VIM shortcuts
C-j, C-k, C-h, C-l to walk splits
:sv <newfile> for horizontal split bottom, :vs <newfile> for vertical split right
:Gbrowse etc for git through vim-fugitive


Steps to install S3FS

wget https://github.com/libfuse/libfuse/releases/download/fuse-3.0.0/fuse-3.0.0.tar.gz
./configure
make && make install

wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/s3fs/s3fs-1.74.tar.gz
make && make install

http://tecadmin.net/mount-s3-bucket-centosrhel-ubuntu-using-s3fs/#

ubuntu@lemp4:/usr/src/s3fs-1.74 ⟫ echo AWS_ACCESS_KEY_ID:AWS_SECRET_ACCESS_KEY > ~/.passwd-s3fs
ubuntu@lemp4:/usr/src/s3fs-1.74 ⟫ chmod 600 ~/.passwd-s3fs


sudo apt-get install libfuse-dev libcurl4-openssl-dev libxml++2.6-dev libssl-dev
