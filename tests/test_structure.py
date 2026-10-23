import pathlib,sys,struct,unittest
BASE=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
import structure as m

def reference(key,value,typ=0):return m._property(key,struct.pack('<Q',value),typ,0x12)

def fixture(inactive=0,completed=1,count=1,padding=0,extra_groups=0,duplicate_quest=False):
    record=m.make_intro_record().replace(struct.pack('<Q',m.UFO),struct.pack('<Q',0x111111))
    group=m._object(m.GROUP,[reference(0xAC016BC1,m.FRONTIERS,0xC0576C2D),m._array(m.MISSION,m.MISSION,[record])])
    groups=[m._object(m.GROUP,[reference(0xAC016BC1,0x222000+i,0xC0576C2D),m._array(m.MISSION,m.MISSION,[])]) for i in range(extra_groups)]+[group]
    history=m._object(m.HISTORY,[m._property(0x387380BA,struct.pack('<Q',1),0x536CB2B3,0x19),m._array(0x72500739,m.GROUP,groups)])
    history_property=m._property(0xC23AA2E9,bytes(14)+history+bytes(4),m.HISTORY,0x13)
    quest=m._object(m.ENTRY,[reference(0x5B6A6F41,m.QUEST),m._property(0x72A56CB6,bytes([inactive])),
          m._property(0xB809DECD,bytes([completed])),m._property(0xCEBFA9E3,struct.pack('<I',count),kind=7)])
    quest_property=m._property(0x12345678,quest)
    properties=[m._property(0x1234,bytes(padding)),history_property,quest_property]
    if duplicate_quest:properties.append(quest_property)
    return bytes(14)+m._object(m.ROOT,properties)+bytes(4)

class StructureTests(unittest.TestCase):
    def test_template_length_and_roundtrip(self):
        record=m.make_intro_record();self.assertEqual(len(record),272)
        obj=m.parse_object(record,0,m.MISSION)
        self.assertEqual(obj.end,272)
        steps=m.parse_array(record,next(p for p in obj.properties if p.typ==m.STEP))
        self.assertEqual(len(steps),1)
        self.assertEqual(m.reference(record,m.prop(steps[0],0xE38B5102)),m.INTRO)

    def test_dynamic_offsets_and_group_counts(self):
        for padding in [0,1,257,32770]:
            for groups in [0,1,19]:
                with self.subTest(padding=padding,groups=groups):
                    source=fixture(padding=padding,extra_groups=groups)
                    result,details=m.apply_repair(source)
                    self.assertEqual(details['status'],'repaired')
                    self.assertEqual(len(result)-len(source),291)
                    analysis=m.analyze(result)
                    self.assertEqual(analysis['group_count'],groups+1)
                    self.assertEqual(analysis['mission_count'],2)
                    self.assertEqual(analysis['quest'],m.analyze(source)['quest'])

    def test_idempotent(self):
        fixed,_=m.apply_repair(fixture());again,details=m.apply_repair(fixed)
        self.assertEqual(fixed,again);self.assertEqual(details['status'],'already_repaired')

    def test_unsupported_quest_states_do_not_change(self):
        for flags in [(1,1,1),(0,0,1),(0,1,0),(0,1,2)]:
            source=fixture(*flags);result,details=m.apply_repair(source)
            self.assertEqual(source,result);self.assertEqual(details['status'],'unsupported')

    def test_completed_not_modified(self):
        fixed,_=m.apply_repair(fixture());b=bytearray(fixed)
        context=m._context(fixed);missions,refs=context[6:8]
        target=missions[refs.index(m.UFO)];score=m.prop(target,0x44E5B54C)
        struct.pack_into('<I',b,score.end-4,100)
        output,details=m.apply_repair(b)
        self.assertEqual(output,bytes(b));self.assertEqual(details['status'],'completed')

    def test_duplicate_accomplishment_rejected(self):
        with self.assertRaises(m.StructureError):m.analyze(fixture(duplicate_quest=True))

    def test_truncation_rejected(self):
        source=fixture()
        for cut in [0,13,25,len(source)-1,len(source)-5]:
            with self.subTest(cut=cut),self.assertRaises(m.StructureError):m.analyze(source[:cut])

    def test_root_length_mismatch_rejected(self):
        b=bytearray(fixture());struct.pack_into('<I',b,18,m.u32(b,18)+1)
        with self.assertRaises(m.StructureError):m.analyze(b)

    def test_corrupt_array_separator_rejected(self):
        b=bytearray(fixture());ctx=m._context(b);mp=ctx[5]
        b[mp.start+22]=1
        with self.assertRaises(m.StructureError):m.analyze(b)

    def test_duplicate_mission_rejected(self):
        fixed,_=m.apply_repair(fixture());ctx=m._context(fixed);missions,refs=ctx[6:8]
        b=bytearray(fixed);other=m.prop(missions[1],0x5FDACBA0)
        b[other.end-8:other.end]=struct.pack('<Q',m.UFO)
        with self.assertRaises(m.StructureError):m.analyze(b)

    def test_source_bytes_untouched(self):
        source=fixture();mutable=bytearray(source);m.apply_repair(mutable)
        self.assertEqual(bytes(mutable),source)


if __name__=='__main__':unittest.main()

