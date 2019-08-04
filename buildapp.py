import docker
import os
import logging
import getopt
import sys

#
# basically a fancy wrapper class
# for dockerclient.images.build()
# to automate building images for my MERN stack
# sample app from
# https://github.com/lucien-stavenhagen/MERN-Stack-Example.git
#
# documentation for the docker SDK for python, which
# is used in this script, is here:
# https://docker-py.readthedocs.io/en/stable/index.html
#


class DockerBuildWrapper:
    def __init__(self, repository, tag, nocache, pull):
        self.dockerclient = docker.from_env()
        self.nocache = nocache
        self.pull = pull
        self.client_dockerfile = os.path.join(os.curdir, "react-client")
        self.server_dockerfile = os.path.join(os.curdir, "rest-server")
        self.logfilename = os.path.join(os.curdir, "dockerbuild.log")
        self.__initTags(repository, tag)
        self.__initLogger()
    #
    # this is to build repository names
    # like foobar/rest-server:tagbar for
    # rest-server and react-client
    #

    def __initTags(self, repository, tag):
        self.server_tag = "{repo}/rest-server".format(repo=repository)
        self.client_tag = "{repo}/react-client".format(repo=repository)
        if tag is not None:
            self.server_tag += ":{0}".format(tag)
            self.client_tag += ":{0}".format(tag)

    def __initLogger(self):
        logging.basicConfig(filename=self.logfilename,
                            filemode="w", level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    #
    # try to slightly translate the logging output
    # returned from dockerclient.images.build()
    # and put it in a Python logger
    #

    def __decodeLogs(self, log_generator_object):
        for log_dict in log_generator_object:
            for key in log_dict.keys():
                self.logger.info("{0}: {1}".format(key, log_dict[key]))

    def __buildImage(self, dockerfile, tag):
        try:
            self.logger.info(
                "building from Dockerfile at {0}...".format(dockerfile))
            new_image, logs = self.dockerclient.images.build(
                path=dockerfile, tag=tag, nocache=self.nocache, pull=self.pull, rm=True)
            self.__decodeLogs(logs)
            self.logger.info("created image. ID: {0}".format(new_image.id))
        except docker.errors.BuildError as berror:
            self.logger.error("build error: {0}".format(berror))
        except docker.errors.APIError as apierror:
            self.logger.error("general api error: {0}".format(apierror))

    def buildRestServer(self):
        self.__buildImage(self.server_dockerfile, self.server_tag)

    def buildReactClient(self):
        self.__buildImage(self.client_dockerfile, self.client_tag)


def usage():
    print("usage: python3 " + sys.argv[0] + " [options]\nRequired:\n\tONE OF OR BOTH:\n\t--client [build React front end client image]\n\t--server [build NodeJS/Express REST backend image]\nOptional:\n\t--tag [specific tag number of image]\n\t--repo [repository prefix]\n\t--nocache [dont use cache in docker build]\n\t--pull [force pull of image in FROM]\n\t-h, --help [this message]")


def main():
    if len(sys.argv) <= 1:
        usage()
        sys.exit(-1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [
            "tag=", "repo=", "nocache", "pull", "help", "client", "server"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(-1)
    tag = None
    pull = False
    repo = "lstavenhagen"
    nocache = False
    react_client = False
    rest_server = False

    for opt, arg in opts:
        if opt == "--tag":
            tag = arg
        elif opt == "--repo":
            repo = arg
        elif opt == "--client":
            react_client = True
        elif opt == "--server":
            rest_server = True
        elif opt == "--nocache":
            nocache = True
        elif opt == "--pull":
            pull = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(-1)
        else:
            assert False, "option {0} not handled".format(opt)

    wrapper = DockerBuildWrapper(
        repository=repo, tag=tag, nocache=nocache, pull=pull)
    if rest_server:
        wrapper.buildRestServer()
    if react_client:
        wrapper.buildReactClient()


if __name__ == "__main__":
    main()
