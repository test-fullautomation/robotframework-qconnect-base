#  Copyright 2020-2022 Robert Bosch Car Multimedia GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup, find_packages

ROOT = dirname(abspath(__file__))

version_file = join(ROOT, 'QConnectionLibrary', 'version.py')
exec(compile(open(version_file).read(), version_file, 'exec'))

setup(
      name='robotframework-qconnect-baselibrary',
      version=VERSION,
      description='Robot Framework testing library for TCP, SSH, Serial Connection',
      long_description=open(join(ROOT, 'README.md')).read(),
      author='Nguyen Huynh Tri Cuong, Thomas Pollerspoeck',
      author_email='cuong.nguyenhuynhtri@vn.bosch.com, thomas.pollerspoeck@de.bosch.com',
      url='https://sourcecode.socialcoding.bosch.com/projects/ROBFW/repos/robotframework-qconnect-base/browse',
      # license='Apache License 2.0',
      keywords='robotframework testing connection ssh tcp serial',
      platforms='any',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      setup_requires=[
      ],
      install_requires=[
          'paramiko >= 2.7.2',
          'robotframework >= 3.2rc2'
      ],
      tests_require=[
      ],
      packages=find_packages(exclude=["demo", "docs", "tests", ]),
      include_package_data=True,
     )
