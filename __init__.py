# -*- coding: utf-8 -*-
# Copyright (c) 2024 Manuel Schneider
# Copyright (c) 2018-2023 Thomas Queste
# Copyright (c) 2023 Valentin Maerten

from dataclasses import dataclass
from pathlib import Path
from typing import Union, List
from shutil import which
from sys import platform
from xml.etree import ElementTree
from albert import *

md_iid = "5.0"
md_version = "4.3.1"
md_name = "Jetbrains projects"
md_description = "Open your JetBrains projects"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/albert-plugin-python-jetbrains-projects"
md_readme_url = "https://github.com/albertlauncher/albert-plugin-python-jetbrains-projects/blob/main/README.md"
md_authors = ["@tomsquest", "@vmaerten", "@ManuelSchneid3r", "@d3v2a"]
md_maintainers = ["@tomsquest", "@vmaerten", "@albi005"]


@dataclass
class Project:
    name: str
    path: str
    last_opened: int
    ide: JetBrainsIde


class JetBrainsIde:
    name: str
    icon: Path
    config_dir_prefixes: list[str]
    binary: str

    def __init__(self, name: str, icon: Path, config_dir_prefixes: list[str], binaries: list[str]):
        self.name = name
        self.icon = icon
        self.config_dir_prefixes = config_dir_prefixes
        self.binary = self._find_binary(binaries)

    @staticmethod
    def _find_binary(binaries: list[str]) -> Union[str, None]:
        for binary in binaries:
            if which(binary):
                return binary
        return None

    @staticmethod
    def _config_dir() -> Path:
        if platform == "darwin":
            return Path.home() / "Library" / "Application Support"
        else:
            return Path.home() / ".config"

    def _get_recent_projects_entries(self, config_dir: Path) -> list[ElementTree.Element]:
        recent_projects_file = Path(config_dir) / "options" / "recentProjects.xml"
        root = ElementTree.parse(recent_projects_file).getroot()
        return root.findall(".//component[@name='RecentProjectsManager']//entry[@key]")

    def _parse_project_entries(self, project_entries: list[ElementTree.Element]) -> list[Project]:
        projects = []
        for entry in project_entries:
            project_path = entry.attrib["key"]
            project_path = project_path.replace("$USER_HOME$", str(Path.home()))
            project_name = Path(project_path).name
            files = Path(project_path + "/.idea").glob("*.iml")
            tag_opened = entry.find(".//option[@name='projectOpenTimestamp']")
            last_opened = tag_opened.attrib["value"] if tag_opened is not None and "value" in tag_opened.attrib else None

            if project_path and last_opened:
                projects.append(Project(name=project_name, path=project_path, last_opened=int(last_opened), ide=self))
            for file in files:
                name = file.name.replace(".iml", "")
                if name != project_name:
                    projects.append(Project(name=name, path=project_path, last_opened=int(last_opened), ide=self))

        return projects

    def list_projects(self) -> List[Project]:
        for config_dir_prefix in self.config_dir_prefixes:
            dirs = list(self._config_dir().glob(f"{config_dir_prefix}*/"))
            if dirs:
                try:
                    recent_projects_entries = self._get_recent_projects_entries(sorted(dirs)[-1])
                    return self._parse_project_entries(recent_projects_entries)
                except (ElementTree.ParseError, FileNotFoundError):
                    return []
        return []

    @staticmethod
    def get_editors(icons_dir: Path) -> List[JetBrainsIde]:
        editors = [
            JetBrainsIde(
                name="Android Studio",
                icon=icons_dir / "androidstudio.svg",
                config_dir_prefixes=["Google/AndroidStudio"],
                binaries=["studio", "androidstudio", "android-studio", "android-studio-canary", "jdk-android-studio",
                          "android-studio-system-jdk"]),
            JetBrainsIde(
                name="Aqua",
                icon=icons_dir / "aqua.svg",
                config_dir_prefixes=["JetBrains/Aqua"],
                binaries=["aqua", "aqua-eap"]),
            JetBrainsIde(
                name="CLion",
                icon=icons_dir / "clion.svg",
                config_dir_prefixes=["JetBrains/CLion"],
                binaries=["clion", "clion-eap"]),
            JetBrainsIde(
                name="DataGrip",
                icon=icons_dir / "datagrip.svg",
                config_dir_prefixes=["JetBrains/DataGrip"],
                binaries=["datagrip", "datagrip-eap"]),
            JetBrainsIde(
                name="DataSpell",
                icon=icons_dir / "dataspell.svg",
                config_dir_prefixes=["JetBrains/DataSpell"],
                binaries=["dataspell", "dataspell-eap"]),
            JetBrainsIde(
                name="GoLand",
                icon=icons_dir / "goland.svg",
                config_dir_prefixes=["JetBrains/GoLand"],
                binaries=["goland", "goland-eap"]),
            JetBrainsIde(
                name="IntelliJ IDEA",
                icon=icons_dir / "idea.svg",
                config_dir_prefixes=["JetBrains/IntelliJIdea", "JetBrains/Idea"],
                binaries=["idea", "idea.sh", "idea-ultimate", "idea-ce-eap", "idea-ue-eap", "intellij-idea-ce",
                          "intellij-idea-ce-eap", "intellij-idea-ue-bundled-jre", "intellij-idea-ultimate-edition",
                          "intellij-idea-community-edition-jre", "intellij-idea-community-edition-no-jre"]),
            JetBrainsIde(
                name="PhpStorm",
                icon=icons_dir / "phpstorm.svg",
                config_dir_prefixes=["JetBrains/PhpStorm"],
                binaries=["phpstorm", "phpstorm-eap"]),
            JetBrainsIde(
                name="PyCharm",
                icon=icons_dir / "pycharm.svg",
                config_dir_prefixes=["JetBrains/PyCharm"],
                binaries=["charm", "pycharm", "pycharm-eap", "pycharm-professional"]),
            Rider(
                name="Rider",
                icon=icons_dir / "rider.svg",
                config_dir_prefixes=["JetBrains/Rider"],
                binaries=["rider", "rider-eap"]),
            JetBrainsIde(
                name="RubyMine",
                icon=icons_dir / "rubymine.svg",
                config_dir_prefixes=["JetBrains/RubyMine"],
                binaries=["rubymine", "rubymine-eap", "jetbrains-rubymine", "jetbrains-rubymine-eap"]),
            JetBrainsIde(
                name="RustRover",
                icon=icons_dir / "rustrover.svg",
                config_dir_prefixes=["JetBrains/RustRover"],
                binaries=["rustrover", "rustrover-eap"]),
            JetBrainsIde(
                name="WebStorm",
                icon=icons_dir / "webstorm.svg",
                config_dir_prefixes=["JetBrains/WebStorm"],
                binaries=["webstorm", "webstorm-eap"]),
            JetBrainsIde(
                name="Writerside",
                icon=icons_dir / "writerside.svg",
                config_dir_prefixes=["JetBrains/Writerside"],
                binaries=["writerside", "writerside-eap"]),
        ]
        return [e for e in editors if e.binary is not None]


class Rider(JetBrainsIde):

    def _get_recent_projects_entries(self, config_dir: Path) -> list[ElementTree.Element]:
        # Rider calls recentProjects.xml -> recentSolutions.xml and
        # in it RecentProjectsManager -> RiderRecentProjectsManager
        recent_projects_file = Path(config_dir) / "options" / "recentSolutions.xml"
        root = ElementTree.parse(recent_projects_file).getroot()
        return root.findall(".//component[@name='RiderRecentProjectsManager']//entry[@key]")


class Plugin(PluginInstance, GeneratorQueryHandler):

    executables = []

    def __init__(self):
        PluginInstance.__init__(self)
        GeneratorQueryHandler.__init__(self)

        self.fuzzy = False

        self._match_path = self.readConfig('match_path', bool)
        if self._match_path is None:
            self._match_path = False

        self.editors = JetBrainsIde.get_editors(Path(__file__).parent / "icons")

    @property
    def match_path(self):
        return self._match_path

    @match_path.setter
    def match_path(self, value):
        self._match_path = value
        self.writeConfig('match_path', value)

    def supportsFuzzyMatching(self):
        return True

    def setFuzzyMatching(self, enabled):
        self.fuzzy = enabled

    def defaultTrigger(self):
        return "jb "

    def _get_projects(self):
        return [
            project
            for editor in self.editors
            for project in editor.list_projects()
            if Path(project.path).exists()
        ]

    def items(self, ctx):
        editor_project_pairs = []

        matcher = Matcher(ctx.query, MatchConfig(fuzzy=self.fuzzy))
        matches = [
            project for project in self._get_projects()
            if matcher.match(*[project.name, project.path] if self._match_path else [project.name])
        ]

        # sort by last opened
        matches.sort(key=lambda p: p.last_opened, reverse=True)

        yield [self._make_item(project) for project in matches]

    @staticmethod
    def _make_item(editor: Editor, project: Project) -> Item:
        return StandardItem(
            id="%s-%s-%s" % (editor.binary, project.path, project.last_opened),
            text=project.name,
            subtext=project.path,
            input_action_text=project.name,
            icon_factory=lambda: Icon.image(str(editor.icon)),
            actions=[
                Action(
                    "Open",
                    "Open in %s" % editor.name,
                    lambda selected_project=project.path: runDetachedProcess(
                        [editor.binary, selected_project]
                    ),
                )
            ],
        )

    def configWidget(self):
        return [
            {
                'type': 'checkbox',
                'property': 'match_path',
                'label': 'Match path'
            }
        ]
