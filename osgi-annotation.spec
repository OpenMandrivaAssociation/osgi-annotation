Name:		osgi-annotation
Version:	8.1.0
Release:	1
Summary:	Annotations for compiling OSGi bundles
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
# Release source from Maven Central. Git-SHA ebe988342384ebafa6a1c6ecae843778617face5.
Source0:	https://repo1.maven.org/maven2/org/osgi/osgi.annotation/%{version}/osgi.annotation-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/ebe988342384ebafa6a1c6ecae843778617face5/LICENSE#/osgi-annotation-%{version}-LICENSE
Source2:	https://raw.githubusercontent.com/osgi/osgi/ebe988342384ebafa6a1c6ecae843778617face5/NOTICE#/osgi-annotation-%{version}-NOTICE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name osgi.annotation --link %{name} --alias org.osgi:org.osgi.annotation --alias org.osgi:org.osgi.annotation.versioning --alias org.osgi:org.osgi.annotation.bundle

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
Annotations for compiling OSGi bundles. 8.1.0 replaces 6.0.0 and is the
combined org.osgi:osgi.annotation jar. It contains the versioning
annotations (package 1.1.2) and the bundle annotations (package 2.0):
Version, ProviderType, ConsumerType, Export, Requirement, Capability,
and the other package annotations. Those sources match
org.osgi.annotation.versioning 1.1.2 and org.osgi.annotation.bundle
2.0.0, and those coordinates are aliases of this jar. The annotations
are not retained at runtime. There are no third-party dependencies.
This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
cp -p %{SOURCE2} NOTICE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

java_files = list(Path("src/main/java").rglob("*.java"))
if len(java_files) != 15:
    raise SystemExit("java files " + str(len(java_files)))
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>osgi.annotation</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>org.osgi:osgi.annotation</name>
  <description>OSGi Annotation Release 8, annotations for compiling bundles.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
poms = sorted(str(path) for path in Path(".").rglob("pom.xml"))
if poms != ["pom.xml"]:
    raise SystemExit("poms " + str(poms))
for needle in (
    "<artifactId>osgi.annotation</artifactId>",
    "<version>%{version}</version>",
    "<release>8</release>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "felix", "maven-bundle-plugin"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/osgi.annotation-%{version}.jar --describe-module osgi.annotation > module-describe.txt
grep -q '^osgi.annotation' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE NOTICE
