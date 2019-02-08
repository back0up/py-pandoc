from setuptools import setup
from setuptools.command.install import install
import os
import os.path as p
import platform
import shutil

src_dir = p.dirname(p.abspath(__file__))


def assert_64_bit_os():
    if not (platform.machine().endswith('64') or  # 64 bit OS if method is OK
            platform.architecture()[0] == '64bit'):  # 64 bit Python
        raise RuntimeError('Only 64bit OS is supported.')


# ------------------------------------------------------------------------------
# Custom settings:
# ------------------------------------------------------------------------------
assert_64_bit_os()
version = '2.5'
tmp = 'tmp'
spec = dict(
    Windows=dict(
        os='win', move=[('Library/bin', tmp)], version=version, build=1,
        hash='a0f6d961e5cc45541be0b0664317295cc870180e2328fa18d2ea481c5079530a'),  # 2.5-1
        # hash='04f1a3e6b05714627872fade3301c3cb057494282ce3a5cb8febab0bc29317d4'),  # 2.6-0
    Linux=dict(
        os='linux', move=[('bin', tmp)], version=version, build=1,
        hash='439737fb9a8e98e36e2a75a62b5fd4c3330e4238bcef6d36353994b7691a37ad'),  # 2.5-1
        # hash='344b57466e76d50e5519823ba385aae50fc42683c933d6c17d9f47fed41cfbf9'),  # 2.6-0
    Darwin=dict(
        os='osx', move=[('bin', tmp)], version=version, build=1,
        hash='d2fa53afdbac6fdf9ba1e44727ccef230ae3300d8ce62db262195d804e53a160'),  # 2.5-1
        # hash='92319289025f2d79a2a69292364121c8e171c57d734a82fa5b2f1eca86e8f9ad'),  # 2.6-0
)[platform.system()]
url = 'https://anaconda.org/conda-forge/pandoc/{version}/download/{os}-64/pandoc-{version}-{build}.tar.bz2'.format(**spec)


class PostInstallCommand(install):
    def run(self):
        excract_tar_and_move_files(url=url, **spec)
        move_contents(
            from_=p.join(src_dir, tmp),
            to=self.install_scripts,
            set_exec=True)
        install.run(self)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


def move_contents(from_, to, set_exec=False):
    import stat
    os.makedirs(to, exist_ok=True)
    for file in os.listdir(from_):
        to_file = p.join(to, file)
        shutil.move(p.join(from_, file),
                    to_file if p.isfile(to_file) else to)
        if p.isfile(to_file) and set_exec:
            if os.name != 'nt':
                st = os.stat(to_file)
                os.chmod(to_file, st.st_mode | stat.S_IEXEC)


def sha256(filename):
    """ https://stackoverflow.com/a/44873382/9071377 """
    import hashlib
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def excract_tar_and_move_files(url, hash, move, **kwargs):
    """
    Moves relative to the setup.py dir. Can download more packages
    if the target archive contains setup.py

    * ``url`` should be of the form z/name.x.y.gz
      (gz, bz2 or other suffix supported by the tarfile module).
    * ``move`` contains pairs of dirs where to move contents.
      First dir is in the extracted archive,
      second dir is in the same folder as setup.py
    """
    import sys
    import tarfile
    from subprocess import call, run, PIPE
    import tempfile

    dirpath = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(dirpath)

    call([sys.executable, "-m", "pip", "download", url], stdout=PIPE, stderr=PIPE)
    filename = url.split('/')[-1]
    ext = p.splitext(filename)[1][1:]
    if sha256(filename) != hash:
        raise RuntimeError(f'SHA256 hash does not match for {filename}')
    with tarfile.open(filename, f"r:{ext}") as tar:
        tar.extractall()

    for from_, to in move:
        from_ = p.abspath(p.normpath(from_))
        to = p.normpath(p.join(src_dir, to))
        os.makedirs(to, exist_ok=True)
        for s in os.listdir(from_):
            shutil.move(p.join(from_, s), to)
    os.chdir(cwd)
    shutil.rmtree(dirpath)


setup(
    name='py-pandoc',
    version=version,
    cmdclass={'install': PostInstallCommand},
    python_requires='>=3.6',
    description='Pandoc in pip and conda',
    url='https://github.com/kiwi0fruit/py-pandoc',
    author='kiwi0fruit',
    author_email='peter.zagubisalo@gmail.com',
    license='GPLv2+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
