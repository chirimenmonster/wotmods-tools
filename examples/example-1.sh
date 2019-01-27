#! /bin/sh

origpkgname='1.0.2.1-20180623-autoaim_indicator.zip'
origrelbase='res_mods/1.0.2.1'
modreldir='scripts/client/gui/mods'
modfilebase='mod_autoaim_indicator'
destdir='tmp'
workdir='tmp/wrk'
releasefile='autoaim_indicator_20180623.wotmod'

patchfile=${modfilebase}.patch
targetsrc=${modfilebase}.py
targetdst=${modfilebase}.pyc

releasebase=${destdir}/${origrelbase}

preparedir=${releasebase}/${modreldir}

recompiledfile=${workdir}/${targetdst}

rm -r tmp/res_mods
rm -r ${workdir}

python2 wottool.py unzip -d ${destdir} ${destdir}/${origpkgname}

python2 wottool.py decompile ${releasebase}/${modreldir} ${workdir}

patch -d ${workdir} -i ../src/${patchfile}
  
python2 -m compileall -d ${modreldir} ${workdir}/${targetsrc}

cp -p ${workdir}/${targetdst} ${preparedir}

python2 wottool.py wotmod ${releasebase} ${releasefile}
