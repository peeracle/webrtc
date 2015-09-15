"""
    Copyright 2013 Appurify, Inc
    All rights reserved

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""
from setuptools import setup, find_packages
from appurify import constants

setup(
    name='appurify',
    version=constants.__version__,
    author='Appurify, Inc',
    author_email=constants.__contact__,
    url=constants.__homepage__,
    license=constants.__license__,
    description=constants.__description__,
    long_description=open('README.txt').read().strip(),
    packages=find_packages(),
    install_requires=open('requirements.txt', 'rb').read().strip().split(),
    tests_require=open('requirements-test.txt', 'rb').read().strip().split(),
    entry_points={
        'console_scripts': [
            'appurify-client.py = appurify.client:init',
            'appurify-tunnel.py = appurify.tunnel:init'
        ]
    }
)
