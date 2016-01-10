import unittest
from conans.test.tools import TestClient
from conans.test.utils.cpp_test_files import cpp_hello_conan_files
from nose.plugins.attrib import attr


@attr("slow")
class ConanTestTest(unittest.TestCase):

    def _create(self, client, number, version, deps=None, export=True):
        files = cpp_hello_conan_files(number, version, deps)
        client.save(files)
        if export:
            client.run("export lasote/stable")

    def conan_test_test(self):
        client = TestClient()
        files = cpp_hello_conan_files("Hello0", "0.1")
        test_conanfile = '''
from conans import ConanFile, CMake
import os

class HelloReuseConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "Hello0/0.1@ lasote/stable"
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake %s' % cmake.command_line)
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        # equal to ./bin/greet, but portable win: .\bin\greet
        self.run(os.sep.join([".","bin", "greet"]))
        '''

        cmakelist = """PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(greet main.cpp)
TARGET_LINK_LIBRARIES(greet ${CONAN_LIBS})
"""
        files["test/CMakeLists.txt"] = cmakelist
        files["test/conanfile.py"] = test_conanfile
        files["test/main.cpp"] = files["main.cpp"]
        client.save(files)
        client.run("export lasote/stable")
        error = client.run("test -s build_type=Release")
        self.assertFalse(error)
        self.assertIn('Hello Hello0', client.user_io.out)
        error = client.run("test -s build_type=Release -o Hello0:language=1")
        self.assertFalse(error)
        self.assertIn('Hola Hello0', client.user_io.out)
