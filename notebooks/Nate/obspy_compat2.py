"""
:module: obspy_compat2.py
:auth: Nathan T. Stevens
:email: ntsteven@uw.edu
:org: Pacific Northwest Seismic Network
:license: GNU GPLv3
:purpose:
    This module complements the pyrocko.obspy_compat.plant method
    to include picks from an ObsPy Catalog object passed to a 
    obspy_compat.snuffle call.
"""
from obspy import Catalog, Stream, UTCDateTime
from obspy.core.event import Pick, QuantityError, WaveformStreamID, ResourceIdentifier
from pyrocko import obspy_compat, model
from pyrocko.gui.snuffler.marker import Marker, EventMarker, PhaseMarker

obspy_compat.plant()

def pick_to_phase(pick, hash=None, kind=0):
    """Convert an obspy Pick object into a snuffler PhaseMarker 

    :param phase: phase marker to convert
    :type phase: pyrocko.gui.snuffler.marker.PhaseMarker
    :return: pick object
    :rtype: obspy.core.event.pick.Pick
    """    
    if pick.evaluation_mode == 'automatic':
        automatic=True
    else:
        automatic=False
    tp = pick.time
    dt = pick.time_errors['uncertainty']
    if isinstance(dt, float):
        tmin = tp - dt
        tmax = tp + dt
    else:
        tmin = tp
        tmax = tp
    
    if hasattr(pick, 'phase_hint'):
        phase_hint = pick.phase_hint
    else:
        phase_hint=None

    pmarker = PhaseMarker(
        tmin=tmin.timestamp,
        tmax=tmax.timestamp,
        nslc_ids=[tuple(pick.waveform_id.id.split('.'))],
        kind=kind,
        event_hash=hash,
        phasename=phase_hint,
        automatic=automatic
    )
    return pmarker

def phase_to_pick(phase):
    """Convert a snuffler PhaseMarker into an obspy Pick object

    :param phase: phase marker to convert
    :type phase: pyrocko.gui.snuffler.marker.PhaseMarker
    :return: pick object
    :rtype: obspy.core.event.pick.Pick
    """    
    if phase.automatic:
        evaluation_mode = 'automatic'
    else:
        evaluation_mode = 'manual'
    
    tmin = phase.tmin
    tmax = phase.tmax
    if tmin == tmax:
        dt = None
        tp = UTCDateTime(tmin)
    else:
        dt = 0.5*(tmax - tmin)
        tp = UTCDateTime(tmin) + dt

    nslc = '.'.join(list(phase.nslc_ids[0]))
    
    pick = Pick(
        resource_id=ResourceIdentifier(prefix='smi:local/eqc_compat/phase_to_pick'),
        time=tp,
        time_errors=QuantityError(uncertainty=dt),
        waveform_id=WaveformStreamID(seed_string=nslc),
        evaluation_mode = evaluation_mode,
        phase_hint=phase.get_phasename()
        )
    return pick

def to_pyrocko_events_and_picks(catalog, altname=None, preferred=True):
    """
    Convert events, preferred origins, and associated picks in an ObsPy
    catalog into collections of pyrocko/snuffler events and markers
    """
    ocat = catalog
    if ocat is None:
        return None
    
    events = []
    markers = []
    for oevent in ocat:
        if preferred:
            origs = [oevent.preferred_origin()]
        else:
            origs = oevent.origins
        for orig in origs:
            if altname is None:
                name = f'{oevent.resource_id}-{orig.resource_id}'
            else:
                name = altname

            event = model.Event(name=name,
                                time=orig.time.timestamp,
                                lat=orig.latitude,
                                lon=orig.longitude,
                                depth=orig.depth,
                                region=orig.region)
            events.append(event)
            emarker = EventMarker(event=event)
            markers.append(emarker)
            hash = emarker.get_event_hash()
            for pick in oevent.picks:
                phase = pick_to_phase(pick, hash=hash)
                markers.append(phase)
    return events, markers