"""Strict structural repair for one identified ACIII Remastered UFO save state.

Only game-format constants are embedded. No account IDs or user save bytes.
The repair reconstructs an accepted quest's Intro history; gameplay success
and quest completion are never granted. Caller handles container encryption.
"""
from dataclasses import dataclass
import struct

ROOT=0x94D6F8F1
HISTORY=0x84A80CC2
GROUP=0xE59D783F
MISSION=0x5ED7B213
STEP=0xF044CBDC
CONSTRAINT=0x12DE6C4C
ENTRY=0x321E790B
UFO=0x2953F22B0
INTRO=0x2953F22BB
FRONTIERS=0x1463028A2
QUEST=0x40BBC940F
ARRAY_MARKER=bytes.fromhex('00001d0a0b01')

class StructureError(ValueError):
    pass

def u32(data,at):
    if at<0 or at+4>len(data):raise StructureError('Truncated 32-bit field')
    return struct.unpack_from('<I',data,at)[0]

@dataclass(frozen=True)
class Property:
    start:int
    size:int
    key:int
    typ:int
    end:int

@dataclass(frozen=True)
class Object:
    start:int
    typ:int
    end:int
    properties:tuple

def parse_object(data,start,expected=None,bound=None):
    limit=len(data) if bound is None else bound
    if start<0 or start+12>limit:raise StructureError('Truncated object header')
    typ,size,total=struct.unpack_from('<III',data,start)
    end=start+4+size
    if expected is not None and typ!=expected:raise StructureError('Unexpected object type')
    if size<8 or total!=size-8 or end>limit:raise StructureError('Invalid object lengths')
    pos=start+12;props=[]
    while pos<end:
        n=u32(data,pos)
        if n<13 or pos+4+n>end:raise StructureError('Invalid property length')
        props.append(Property(pos,n,u32(data,pos+4),u32(data,pos+8),pos+4+n))
        pos+=4+n
    if pos!=end:raise StructureError('Object properties do not meet boundary')
    return Object(start,typ,end,tuple(props))

def one(values,label):
    values=list(values)
    if len(values)!=1:raise StructureError('Expected exactly one '+label)
    return values[0]

def prop(obj,key):return one((p for p in obj.properties if p.key==key),'property '+hex(key))

def scalar(data,p,width):
    if p.size!=13+width or data[p.start+16]!=11:raise StructureError('Unexpected scalar encoding')
    return int.from_bytes(data[p.end-width:p.end],'little')

def reference(data,p):
    if p.size!=21 or data[p.start+16]!=11:raise StructureError('Unexpected reference encoding')
    return int.from_bytes(data[p.end-8:p.end],'little')

def parse_array(data,p,expected=None):
    if p.size<18 or data[p.start+12:p.start+18]!=ARRAY_MARKER:
        raise StructureError('Unsupported array encoding')
    typ=p.typ
    if expected is not None and typ!=expected:raise StructureError('Unexpected array element type')
    count=u32(data,p.start+18)
    # Minimum object header plus separator limits count using actual bytes.
    if count>(p.size//12):raise StructureError('Impossible array count')
    at=p.start+37;objects=[]
    if not count:
        if p.end!=p.start+22:raise StructureError('Unexpected empty array encoding')
        return objects
    if data[p.start+22:p.start+37]!=bytes(15):raise StructureError('Unexpected array prefix')
    for index in range(count):
        obj=parse_object(data,at,typ,p.end);objects.append(obj);at=obj.end
        padding=19 if index<count-1 else 4
        if data[at:at+padding]!=bytes(padding):raise StructureError('Unexpected array separator')
        at+=padding
    if at!=p.end:raise StructureError('Array elements do not meet boundary')
    return objects

def _context(data):
    # State serialization has a 14-byte fixed preamble preceding its root object.
    if len(data)<26 or data[:14]!=bytes(14):raise StructureError('Unsupported state preamble')
    root=parse_object(data,14,ROOT)
    if root.end+4!=len(data) or data[root.end:]!=bytes(4):raise StructureError('Unexpected state root trailer')
    candidates=[]
    for p in root.properties:
        if p.typ!=HISTORY:continue
        # Nullable object reference header: metadata + eight-byte object tag.
        h=parse_object(data,p.start+31,HISTORY,p.end)
        if h.end+4!=p.end or data[h.end:p.end]!=bytes(4):
            raise StructureError('Unexpected MissionHistory wrapper')
        if scalar(data,prop(h,0x387380BA),8)&0xffffffff==1:candidates.append((p,h))
    hp,history=one(candidates,'MissionHistory identifier 1')
    gp=one((p for p in history.properties if p.typ==GROUP),'mission group array')
    groups=parse_array(data,gp,GROUP)
    group=one((g for g in groups if reference(data,prop(g,0xAC016BC1))==FRONTIERS),'Frontiersmen group')
    mp=one((p for p in group.properties if p.typ==MISSION),'mission record array')
    missions=parse_array(data,mp,MISSION)
    refs=[reference(data,prop(m,0x5FDACBA0)) for m in missions]
    if len(set(refs))!=len(refs):raise StructureError('Duplicate mission history entries')
    # Accomplishment entries are independently self-framed and reference the
    # quest via their Id property. Validate complete object/property boundaries.
    needle=struct.pack('<I',ENTRY);at=-1;quests=[]
    while True:
        at=data.find(needle,at+1)
        if at<0:break
        try:
            entry=parse_object(data,at,ENTRY)
            if reference(data,prop(entry,0x5B6A6F41))==QUEST:quests.append(entry)
        except StructureError:continue
    quest=one(quests,'UFO accomplishment entry')
    flags={'inactive':scalar(data,prop(quest,0x72A56CB6),1),
           'completed':scalar(data,prop(quest,0xB809DECD),1),
           'current_count':scalar(data,prop(quest,0xCEBFA9E3),4)}
    return root,hp,history,gp,group,mp,missions,refs,flags

def _inspect(data):
    ctx=_context(data);root,hp,history,gp,group,mp,missions,refs,flags=ctx
    details={'mission_id':hex(UFO),'intro_step_id':hex(INTRO),'quest':flags,
             'mission_count':len(missions),'group_count':len(parse_array(data,gp,GROUP))}
    if UFO in refs:
        m=missions[refs.index(UFO)]
        score=scalar(data,prop(m,0x44E5B54C),4)
        sp=one((p for p in m.properties if p.typ==STEP),'mission step array')
        steps=parse_array(data,sp,STEP)
        intro=[st for st in steps if reference(data,prop(st,0xE38B5102))==INTRO]
        if score:
            details.update(status='completed',reason='UFO mission already has a nonzero score')
        elif len(intro)==1 and scalar(data,prop(intro[0],0x3DF97B36),1)==1:
            details.update(status='already_repaired',reason='UFO Intro history already exists')
        else:details.update(status='unsupported',reason='UFO mission history already exists in another state')
    elif flags=={'inactive':0,'completed':1,'current_count':1}:
        details.update(status='repairable',reason='Accepted UFO quest has no mission history')
    else:details.update(status='unsupported',reason='UFO accomplishment differs from the supported accepted-quest state')
    return details,ctx

def analyze(state):
    """Return supported-state status; malformed/ambiguous structures raise."""
    return _inspect(bytes(state))[0]

def _property(key,payload,typ=0,kind=0):
    body=struct.pack('<II',key,typ)+struct.pack('<HHB',0,kind,11)+payload
    return struct.pack('<I',len(body))+body

def _object(typ,properties):
    body=b''.join(properties)
    return struct.pack('<III',typ,len(body)+8,len(body))+body

def _array(key,typ,objects):
    marker=bytes.fromhex('00009d0a0b01') if typ==CONSTRAINT else ARRAY_MARKER
    metadata=struct.pack('<II',key,typ)+marker+struct.pack('<I',len(objects))
    if objects:metadata+=bytes(15)+bytes(19).join(objects)+bytes(4)
    return struct.pack('<I',len(metadata))+metadata

def make_intro_record():
    """Build a zero-score mission record with only its Intro succeeded."""
    step=_object(STEP,[
        _property(0xE38B5102,struct.pack('<Q',INTRO),0xB3195056,0x12),
        _property(0x1208E3E4,b'\1'),_property(0x3DF97B36,b'\1'),
        _property(0x3FB06AC1,bytes(4),kind=7)])
    record=_object(MISSION,[
        _property(0x5FDACBA0,struct.pack('<Q',UFO),0x5FDACBA0,0x12),
        _property(0x44E5B54C,bytes(4),kind=7),
        _property(0xEB76C432,bytes(4),kind=7),
        _property(0xD47806F0,b'\0'),_property(0x2B7B185F,b'\1'),
        _array(STEP,STEP,[step]),_array(CONSTRAINT,CONSTRAINT,[])])
    if len(record)!=272:raise StructureError('Internal record construction error')
    return record

def apply_repair(state):
    """Return (new_state, details). Unsupported/already repaired returns input."""
    state=bytes(state);details,ctx=_inspect(state)
    if details['status']!='repairable':return state,details
    root,hp,history,gp,group,mp,missions,refs,flags=ctx
    record=make_intro_record();insertion=record+bytes(19)
    if not missions:raise StructureError('Unsupported empty Frontiersmen mission history')
    patched=bytearray(state)
    lengths=[root.start+4,root.start+8,hp.start,history.start+4,
             history.start+8,gp.start,group.start+4,group.start+8,mp.start]
    for offset in lengths:struct.pack_into('<I',patched,offset,u32(state,offset)+len(insertion))
    struct.pack_into('<I',patched,mp.start+18,len(missions)+1)
    at=missions[0].start;patched[at:at]=insertion
    after=analyze(patched)
    if after['status']!='already_repaired':raise StructureError('Repair readback failed')
    details=dict(details,status='repaired',reason='Reconstructed UFO Intro history',bytes_added=len(insertion),
                 mission_count_after=after['mission_count'])
    return bytes(patched),details
