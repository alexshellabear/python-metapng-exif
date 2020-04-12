import os
import struct
import math # Used for floor function

class read_tiff_image_file_header_ifh():
    def __init__(self,data):
        self.byte_order_2_bytes = data[0:2]
        self.version_2_bytes = data[2:4] # Always 42, 0x2A00 or 0x002A (depending upon byte order)
        self.identifier_4_bytes = data[4:8] # Should be a max of 4 bytes

        self.little_endian, _ = self.file_order_from_byte_order(self.byte_order_2_bytes)
        self.check_tiff_file_version(self.version_2_bytes)

        self.first_ifd_offset = self.get_ifd_offset_to_int(self.identifier_4_bytes,data)

    def read_image_file_directories(self,data,little_endian=True):
        ifds = []

        next_ifd_offset_start_slice = self.first_ifd_offset
        while next_ifd_offset_start_slice != 0:
            ifds.append(tiff_image_file_directory_ifd(data,next_ifd_offset_start_slice,little_endian=little_endian))
            next_ifd_offset_start_slice = ifds[-1].next_ifd_offset_int
        return ifds

    def convert_bytes_to_int(self,input_bytes:bytearray,little_endian=True):
        if little_endian:
            return int.from_bytes(input_bytes,byteorder="little",signed=False)
        else:
            return int.from_bytes(input_bytes,byteorder="big",signed=False)

    def file_order_from_byte_order(self,byte_order:bytearray): # TODO put function to read file
        if not(type(byte_order) == bytearray or type(byte_order) == bytes):
            raise TypeError(f"ERROR[read_tiff_image_file_header_ifh.file_order_from_byte_order]: byte_order is not of type bytearray or bytes instead it is of type |{type(byte_order)}|")
        if len(byte_order) != 2:
            raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.file_order_from_byte_order]: byte_order should be a length of 2 bytes, instead it is of length |{len(byte_order)}|")
        
        if byte_order == bytes.fromhex('4949'): # II
            return True, "Little Endian"
        elif byte_order == bytes.fromhex('4D4D'): # MM # TODO confi
            raise ValueError("haven't tackled big endian yet! TODO")
            return False, "Big Endian"
        else:
            raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.file_order_from_byte_order]: Value should be 4D4D (MM) or 4949 (II) not |{byte_order}|")

    def check_tiff_file_version(self,version_2_bytes:bytearray):
        if not(type(version_2_bytes) == bytearray or type(version_2_bytes) == bytes):
            raise TypeError(f"ERROR[read_tiff_image_file_header_ifh.check_tiff_file_version]: version_2_bytes is not of type bytearray or bytes instead it is of type |{type(version_2_bytes)}|")
        if len(version_2_bytes) != 2:
            raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.check_tiff_file_version]: version_2_bytes should be a length of 2 bytes, instead it is of length |{len(version_2_bytes)}|")

        if self.little_endian:
            if version_2_bytes != bytes.fromhex("2A00"):
                raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.check_tiff_file_version]: File does not contain version.. possibly wrong file")
        else:
            if version_2_bytes != bytes.fromhex("002A"):
                raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.check_tiff_file_version]: File does not contain version.. possibly wrong file")
            
    def get_ifd_offset_to_int(self,ifd_offset:bytearray,data):
        if not(type(ifd_offset) == bytearray or type(ifd_offset) == bytes):
            raise TypeError(f"ERROR[read_tiff_image_file_header_ifh.get_ifd_offset_to_int]: ifd_offset is not of type bytearray or bytes instead it is of type |{type(ifd_offset)}|")
        if len(ifd_offset) != 4:
            raise ValueError(f"ERROR[read_tiff_image_file_header_ifh.get_ifd_offset_to_int]: ifd_offset should be a length of 4 bytes, instead it is of length |{len(ifd_offset)}|")

        if ifd_offset == bytes.fromhex('00000000'):
            return None

        return self.convert_bytes_to_int(ifd_offset,little_endian=self.little_endian) 

class tiff_file_data():
    def __init__(self):
        self.is_initialised = True

    def add_raw_image(self,image):
        self.image = image

    def read_file()
        if type(file_path) != str:
            raise TypeError(f"ERROR[tiff_file_data.__init__]: file_path should be type str instead it is |{type(file_path)}|")
        if not (".tif" in file_path or ".tiff" in file_path):
            raise ValueError(f"ERROR[tiff_file_data.__init__]: File extension should be .tiff or .tif instead file path was |{file_path}|")
        file_extension = os.path.splitext(file_path)[1]
        if not(file_extension == ".tif" or file_extension == ".tiff"):
            raise ValueError(f"ERROR[tiff_file_data.__init__]: File extension should be .tiff or .tif instead file extension was |{file_extension}|")
        if os.path.exists(file_path) == False:
            raise ValueError(f"ERROR[tiff_file_data.__init__]: File path |{file_path}| does not exist")
        if os.path.isfile(file_path) == False:
            raise ValueError(f"ERROR[tiff_file_data.__init__]: File path |{file_path}| does is not a file")

        try:
            file_object = open(file_path,"rb")
            try:
                self.data = file_object.read()
            except:
                raise IOError(f"ERROR[tiff_file_data.__init__]: Can't read file |{file_path}|")
            finally:
                file_object.close()
        except:
            raise IOError(f"ERROR[tiff_file_data.__init__]: Can't open file |{file_path}|")

        self.image_file_header_ifh = read_tiff_image_file_header_ifh(self.data)

        self.image_file_directories_ifds = self.image_file_header_ifh.read_image_file_directories(self.data)

        self.image_file_directories_ifds[0].get_all_tags_id_and_data()

class tiff_image_file_directory_ifd():
    def __init__(self,data:bytearray,int_ifd_offset:int,little_endian=True):
        self.tag_number_byte_array = data[int_ifd_offset:int_ifd_offset+2]
        self.tag_number_int = self.convert_bytes_to_int(self.tag_number_byte_array,little_endian=little_endian)

        self.start_ifd_slice = int_ifd_offset
        self.end_ifd_slice = int_ifd_offset + 2 + self.tag_number_int * 12 + 4

        next_ifd_offset_start_slice = int_ifd_offset + 2 + self.tag_number_int * 12
        self.next_ifd_offset_array = data[next_ifd_offset_start_slice:next_ifd_offset_start_slice+4]
        self.next_ifd_offset_int = self.convert_bytes_to_int(self.next_ifd_offset_array,little_endian=little_endian)

        self.tags = []
        for tag_number in range(self.tag_number_int):
            start_slice = int_ifd_offset + 2 + tag_number * 12
            end_slice = start_slice + 12
            tag_byte_array = data[start_slice:end_slice]
            self.tags.append(tiff_tag_class(tag_byte_array,data,little_endian))

        
        # Assume image is not stripped, TODO add this functionallity in later - https://www.fileformat.info/format/tiff/egff.htm
        image_width = self.get_tag_by_id(256).tag_data
        image_length = self.get_tag_by_id(257).tag_data
        rows_per_strip = self.get_tag_by_id(278).tag_data
        strip_offsets = self.get_tag_by_id(273).tag_data # TODO make into an array, or able to handle arrays, modify tag class
        byte_count_per_strip = self.get_tag_by_id(279).tag_data # TODO make into an array, or able to handle arrays, modify tag class

        #number_strips_in_image = math.floor(  (image_length * (rows_per_strip - 1)) / rows_per_strip )
        start_image_slice = strip_offsets
        end_image_slice = strip_offsets+byte_count_per_strip+1
        self.bitmap_byte_array = data[start_image_slice:end_image_slice]

    def get_start_and_end_external_tag_data_slices(self):
        # Assume that tag data is a continuous block
        start_slice = 99999999999999
        end_slice = 0
        for tag in self.tags:
            if tag.does_tag_use_external_data() == True:
                if tag.data_offset < start_slice:
                    start_slice = tag.data_offset
                if tag.data_offset + tag.number_bytes_tag_data > end_slice:
                    end_slice = tag.data_offset + tag.number_bytes_tag_data
        return (start_slice,end_slice)



    def get_all_tags_id_and_data(self):
        tag_id_and_data = []
        for tag in self.tags:
            tag_id_and_data.append(tag.get_tag_id_and_data())
            print(tag_id_and_data[-1])

    def get_tag_by_id(self,search_id:int):
        if type(search_id) != int:
            raise TypeError(f"ERROR[tiff_image_file_directory_ifd.get_tag_by_id]: search_id should be type int, instead it is {type(search_id)}")
        for tag in self.tags:
            if tag.tag_id == search_id:
                return tag
        return None

    def convert_bytes_to_int(self,input_bytes:bytearray,little_endian=True):
        if little_endian:
            return int.from_bytes(input_bytes,byteorder="little",signed=False)
        else:
            return int.from_bytes(input_bytes,byteorder="big",signed=False)
            
    def get_compression_type(self,compression_int:int):
        # Note 1: Source https://www.awaresystems.be/imaging/tiff/tifftags/compression.html
        if type(compression_int) != int:
            raise TypeError(f"ERROR[tiff_image_file_directory_ifd.get_compression_type]: compression_int should be type int, instead it is {type(compression_int)}")

        if compression_int == 1:
            return "No Compression"
        elif compression_int == 2:
            return "CCITT modified Huffman RLE"
        elif compression_int == 3:
            return "CCITT Group 3 fax encoding"
        elif compression_int == 4:
            return "CCITT Group 4 fax encoding"
        elif compression_int == 5:
            return "LZW - Propriety Compression Algorithm"
        elif compression_int == 6:
            return "JPEG ('old-style' JPEG, later overridden in Technote2)"
        elif compression_int == 7:
            return "JPEG ('new-style' JPEG)"
        elif compression_int == 8:
            return "Deflate ('Adobe-style')"
        elif compression_int == 9:
            return "Defined by TIFF-F and TIFF-FX standard (RFC 2301) as ITU-T Rec. T.82 coding, using ITU-T Rec. T.85 (which boils down to JBIG on black and white)"
        elif compression_int == 10: 
            return "Defined by TIFF-F and TIFF-FX standard (RFC 2301) as ITU-T Rec. T.82 coding, using ITU-T Rec. T.43 (which boils down to JBIG on color)"
        elif compression_int == 333:
            return "Custom PNG - Specifically for this project"
        else:
            return ValueError("ERROR[tiff_image_file_directory_ifd.get_compression_type]: compression_int did not match any of the coded compression types, see function elif statement")
class tiff_tag_class():
    data_type_dictionary = {
        1:"BYTE"
        ,2:"ASCII"
        ,3:"SHORT"
        ,4:"LONG"
        ,5:"RATIONAL"
        ,6:"SBYTE"
        ,7:"UNDEFINE"
        ,8:"SSHORT"
        ,9:"SLONG"
        ,10:"SRATIONAL"
        ,11:"FLOAT"
        ,12:"DOUBLE"
    }
    tag_id_dictionary= {
        11: 'ProcessingSoftware'
        , 254: 'NewSubfileType'
        , 255: 'SubfileType'
        , 256: 'ImageWidth'
        , 257: 'ImageLength'
        , 258: 'BitsPerSample'
        , 259: 'Compression'
        , 262: 'PhotometricInterpretation'
        , 263: 'Thresholding'
        , 264: 'CellWidth'
        , 265: 'CellLength'
        , 266: 'FillOrder'
        , 269: 'DocumentName'
        , 270: 'ImageDescription'
        , 271: 'Make'
        , 272: 'Model'
        , 273: 'StripOffsets'
        , 274: 'Orientation'
        , 277: 'SamplesPerPixel'
        , 278: 'RowsPerStrip'
        , 279: 'StripByteCounts'
        , 280: 'MinSampleValue'
        , 281: 'MaxSampleValue'
        , 282: 'XResolution'
        , 283: 'YResolution'
        , 284: 'PlanarConfiguration'
        , 285: 'PageName'
        , 288: 'FreeOffsets'
        , 289: 'FreeByteCounts'
        , 290: 'GrayResponseUnit'
        , 291: 'GrayResponseCurve'
        , 292: 'T4Options'
        , 293: 'T6Options'
        , 296: 'ResolutionUnit'
        , 297: 'PageNumber'
        , 301: 'TransferFunction'
        , 305: 'Software'
        , 306: 'DateTime'
        , 315: 'Artist'
        , 316: 'HostComputer'
        , 317: 'Predictor'
        , 318: 'WhitePoint'
        , 319: 'PrimaryChromaticities'
        , 320: 'ColorMap'
        , 321: 'HalftoneHints'
        , 322: 'TileWidth'
        , 323: 'TileLength'
        , 324: 'TileOffsets'
        , 325: 'TileByteCounts'
        , 330: 'SubIFDs'
        , 332: 'InkSet'
        , 333: 'InkNames'
        , 334: 'NumberOfInks'
        , 336: 'DotRange'
        , 337: 'TargetPrinter'
        , 338: 'ExtraSamples'
        , 339: 'SampleFormat'
        , 340: 'SMinSampleValue'
        , 341: 'SMaxSampleValue'
        , 342: 'TransferRange'
        , 343: 'ClipPath'
        , 344: 'XClipPathUnits'
        , 345: 'YClipPathUnits'
        , 346: 'Indexed'
        , 347: 'JPEGTables'
        , 351: 'OPIProxy'
        , 512: 'JPEGProc'
        , 513: 'JpegIFOffset'
        , 514: 'JpegIFByteCount'
        , 515: 'JpegRestartInterval'
        , 517: 'JpegLosslessPredictors'
        , 518: 'JpegPointTransforms'
        , 519: 'JpegQTables'
        , 520: 'JpegDCTables'
        , 521: 'JpegACTables'
        , 529: 'YCbCrCoefficients'
        , 530: 'YCbCrSubSampling'
        , 531: 'YCbCrPositioning'
        , 532: 'ReferenceBlackWhite'
        , 700: 'XMLPacket'
        , 4096: 'RelatedImageFileFormat'
        , 4097: 'RelatedImageWidth'
        , 4098: 'RelatedImageLength'
        , 18246: 'Rating'
        , 18249: 'RatingPercent'
        , 32781: 'ImageID'
        , 33421: 'CFARepeatPatternDim'
        , 33422: 'CFAPattern'
        , 33423: 'BatteryLevel'
        , 33432: 'Copyright'
        , 33434: 'ExposureTime'
        , 33437: 'FNumber'
        , 33723: 'IPTCNAA'
        , 34377: 'ImageResources'
        , 34665: 'ExifOffset'
        , 34675: 'InterColorProfile'
        , 34850: 'ExposureProgram'
        , 34852: 'SpectralSensitivity'
        , 34853: 'GPSInfo'
        , 34855: 'ISOSpeedRatings'
        , 34856: 'OECF'
        , 34857: 'Interlace'
        , 34858: 'TimeZoneOffset'
        , 34859: 'SelfTimerMode'
        , 36864: 'ExifVersion'
        , 36867: 'DateTimeOriginal'
        , 36868: 'DateTimeDigitized'
        , 37121: 'ComponentsConfiguration'
        , 37122: 'CompressedBitsPerPixel'
        , 37377: 'ShutterSpeedValue'
        , 37378: 'ApertureValue'
        , 37379: 'BrightnessValue'
        , 37380: 'ExposureBiasValue'
        , 37381: 'MaxApertureValue'
        , 37382: 'SubjectDistance'
        , 37383: 'MeteringMode'
        , 37384: 'LightSource'
        , 37385: 'Flash'
        , 37386: 'FocalLength'
        , 37387: 'FlashEnergy'
        , 37388: 'SpatialFrequencyResponse'
        , 37389: 'Noise'
        , 37393: 'ImageNumber'
        , 37394: 'SecurityClassification'
        , 37395: 'ImageHistory'
        , 37396: 'SubjectLocation'
        , 37397: 'ExposureIndex'
        , 37398: 'TIFF/EPStandardID'
        , 37500: 'MakerNote'
        , 37510: 'UserComment'
        , 37520: 'SubsecTime'
        , 37521: 'SubsecTimeOriginal'
        , 37522: 'SubsecTimeDigitized'
        , 40091: 'XPTitle'
        , 40092: 'XPComment'
        , 40093: 'XPAuthor'
        , 40094: 'XPKeywords'
        , 40095: 'XPSubject'
        , 40960: 'FlashPixVersion'
        , 40961: 'ColorSpace'
        , 40962: 'ExifImageWidth'
        , 40963: 'ExifImageHeight'
        , 40964: 'RelatedSoundFile'
        , 40965: 'ExifInteroperabilityOffset'
        , 41483: 'FlashEnergy'
        , 41484: 'SpatialFrequencyResponse'
        , 41486: 'FocalPlaneXResolution'
        , 41487: 'FocalPlaneYResolution'
        , 41488: 'FocalPlaneResolutionUnit'
        , 41492: 'SubjectLocation'
        , 41493: 'ExposureIndex'
        , 41495: 'SensingMethod'
        , 41728: 'FileSource'
        , 41729: 'SceneType'
        , 41730: 'CFAPattern'
        , 41985: 'CustomRendered'
        , 41986: 'ExposureMode'
        , 41987: 'WhiteBalance'
        , 41988: 'DigitalZoomRatio'
        , 41989: 'FocalLengthIn35mmFilm'
        , 41990: 'SceneCaptureType'
        , 41991: 'GainControl'
        , 41992: 'Contrast'
        , 41993: 'Saturation'
        , 41994: 'Sharpness'
        , 41995: 'DeviceSettingDescription'
        , 41996: 'SubjectDistanceRange'
        , 42016: 'ImageUniqueID'
        , 42032: 'CameraOwnerName'
        , 42033: 'BodySerialNumber'
        , 42034: 'LensSpecification'
        , 42035: 'LensMake'
        , 42036: 'LensModel'
        , 42037: 'LensSerialNumber'
        , 42240: 'Gamma'
        , 50341: 'PrintImageMatching'
        , 50706: 'DNGVersion'
        , 50707: 'DNGBackwardVersion'
        , 50708: 'UniqueCameraModel'
        , 50709: 'LocalizedCameraModel'
        , 50710: 'CFAPlaneColor'
        , 50711: 'CFALayout'
        , 50712: 'LinearizationTable'
        , 50713: 'BlackLevelRepeatDim'
        , 50714: 'BlackLevel'
        , 50715: 'BlackLevelDeltaH'
        , 50716: 'BlackLevelDeltaV'
        , 50717: 'WhiteLevel'
        , 50718: 'DefaultScale'
        , 50719: 'DefaultCropOrigin'
        , 50720: 'DefaultCropSize'
        , 50721: 'ColorMatrix1'
        , 50722: 'ColorMatrix2'
        , 50723: 'CameraCalibration1'
        , 50724: 'CameraCalibration2'
        , 50725: 'ReductionMatrix1'
        , 50726: 'ReductionMatrix2'
        , 50727: 'AnalogBalance'
        , 50728: 'AsShotNeutral'
        , 50729: 'AsShotWhiteXY'
        , 50730: 'BaselineExposure'
        , 50731: 'BaselineNoise'
        , 50732: 'BaselineSharpness'
        , 50733: 'BayerGreenSplit'
        , 50734: 'LinearResponseLimit'
        , 50735: 'CameraSerialNumber'
        , 50736: 'LensInfo'
        , 50737: 'ChromaBlurRadius'
        , 50738: 'AntiAliasStrength'
        , 50739: 'ShadowScale'
        , 50740: 'DNGPrivateData'
        , 50741: 'MakerNoteSafety'
        , 50778: 'CalibrationIlluminant1'
        , 50779: 'CalibrationIlluminant2'
        , 50780: 'BestQualityScale'
        , 50781: 'RawDataUniqueID'
        , 50827: 'OriginalRawFileName'
        , 50828: 'OriginalRawFileData'
        , 50829: 'ActiveArea'
        , 50830: 'MaskedAreas'
        , 50831: 'AsShotICCProfile'
        , 50832: 'AsShotPreProfileMatrix'
        , 50833: 'CurrentICCProfile'
        , 50834: 'CurrentPreProfileMatrix'
        , 50879: 'ColorimetricReference'
        , 50931: 'CameraCalibrationSignature'
        , 50932: 'ProfileCalibrationSignature'
        , 50934: 'AsShotProfileName'
        , 50935: 'NoiseReductionApplied'
        , 50936: 'ProfileName'
        , 50937: 'ProfileHueSatMapDims'
        , 50938: 'ProfileHueSatMapData1'
        , 50939: 'ProfileHueSatMapData2'
        , 50940: 'ProfileToneCurve'
        , 50941: 'ProfileEmbedPolicy'
        , 50942: 'ProfileCopyright'
        , 50964: 'ForwardMatrix1'
        , 50965: 'ForwardMatrix2'
        , 50966: 'PreviewApplicationName'
        , 50967: 'PreviewApplicationVersion'
        , 50968: 'PreviewSettingsName'
        , 50969: 'PreviewSettingsDigest'
        , 50970: 'PreviewColorSpace'
        , 50971: 'PreviewDateTime'
        , 50972: 'RawImageDigest'
        , 50973: 'OriginalRawFileDigest'
        , 50974: 'SubTileBlockSize'
        , 50975: 'RowInterleaveFactor'
        , 50981: 'ProfileLookTableDims'
        , 50982: 'ProfileLookTableData'
        , 51008: 'OpcodeList1'
        , 51009: 'OpcodeList2'
        , 51022: 'OpcodeList3'
        , 51041: 'NoiseProfile'
    }
    def __init__(self,tag_data:bytearray,data:bytearray,little_endian=True):
        if not(type(tag_data) == bytearray or type(tag_data) == bytes):
            raise TypeError(f"ERROR[tiff_tag_class.__init__]: byte_order is not of type bytearray or bytes instead it is of type |{type(tag_data)}|")
        if len(tag_data) != 12:
            raise ValueError(f"ERROR[tiff_tag_class.__init__]: byte_order should be a length of 2 bytes, instead it is of length |{len(tag_data)}|")
        if not(type(data) == bytearray or type(data) == bytes):
            raise TypeError(f"ERROR[tiff_tag_class.__init__]: byte_order is not of type bytearray or bytes instead it is of type |{type(data)}|")


        self.tag_id_byte_array = tag_data[0:2] # 2 bytes
        self.tag_id = self.convert_bytes_to_int(self.tag_id_byte_array,little_endian=little_endian)


        self.data_type_byte_array = tag_data[2:4] # 2 bytes
        self.data_type = self.convert_bytes_to_int(self.data_type_byte_array,little_endian=little_endian)
        self.data_count_byte_array = tag_data[4:8] # 4 bytes, the number of items of data type in the data tag
        self.data_count = self.convert_bytes_to_int(self.data_count_byte_array,little_endian=little_endian)
        self.data_offset_byte_array = tag_data[8:12] # 4 bytes, if data doesn't fit into tag then it points to the data
        self.data_offset = self.convert_bytes_to_int(self.data_offset_byte_array,little_endian=little_endian)
        self.tag_data = None

        # TODO convert to function
        self.number_bytes_tag_data = self.get_number_of_bytes_in_data()
        if self.does_tag_use_external_data():
            self.data_offset = self.convert_bytes_to_int(self.data_offset_byte_array,little_endian=little_endian)
            start_slice = self.data_offset
            end_slice = start_slice + self.number_bytes_tag_data
            self.tag_data_byte_array = data[start_slice:end_slice]
            self.tag_data = self.convert_tag_data_byte_array(self.tag_data_byte_array,self.data_type,little_endian=little_endian)
        else:
            self.tag_data_byte_array = self.data_offset_byte_array
            self.tag_data = self.convert_tag_data_byte_array(self.tag_data_byte_array,self.data_type,little_endian=little_endian)

    def does_tag_use_external_data(self):
        if self.number_bytes_tag_data > 4:
            return True
        else:
            return False
    def get_tag_id_and_data(self):
        return (self.tag_id,self.tag_id_dictionary[self.tag_id],self.data_offset,self.tag_data)

    def convert_tag_data_byte_array(self,tag_data_byte_array:bytearray,data_type:int,little_endian=True):
        if type(data_type) != int:
            raise TypeError(f"ERROR[tiff_tag_class.convert_tag_data_byte_array]: data_type is not of type int instead it is of type |{type(data_type)}|")
        if data_type < 1 or data_type > 12:
            raise ValueError(f"ERROR[tiff_tag_class.convert_tag_data_byte_array]: data_type should be between 1-12 instead it was |{data_type}|")
        if not(type(tag_data_byte_array) == bytearray or type(tag_data_byte_array) == bytes):
            raise TypeError(f"ERROR[tiff_tag_class.convert_tag_data_byte_array]: tag_data_byte_array is not of type bytearray or bytes instead it is of type |{type(tag_data_byte_array)}|")

        if type(tag_data_byte_array) == bytes:
            tag_data_byte_array = bytearray(tag_data_byte_array)

        # TODO fix function
        if data_type == 1:
            return None
        elif data_type == 2:
            if little_endian:
                tag_data_byte_array.reverse()
            return tag_data_byte_array.decode("ASCII")
        elif data_type == 3:
            short_return_array = []
            number_of_data_points = int(len(tag_data_byte_array)/2)
            for data_point in range(number_of_data_points):
                temp_short_byte_array = tag_data_byte_array[data_point*2:data_point*2+2]
                short_return_array.append(self.convert_bytes_to_int(temp_short_byte_array,little_endian=little_endian))
            return short_return_array
        elif data_type == 4:
            return self.convert_bytes_to_int(tag_data_byte_array,little_endian=little_endian)
        elif data_type == 5:
            if len(tag_data_byte_array) != 8:
                raise ValueError(f"ERROR[tiff_tag_class.convert_tag_data_byte_array]: tag_data_byte_array be of length 8 instead it was |{len(tag_data_byte_array)}|")
            
            first_real_byte_array = tag_data_byte_array[0:4]
            second_real_byte_array = tag_data_byte_array[4:8]

            first_real_int = self.convert_bytes_to_int(first_real_byte_array,little_endian=little_endian)
            second_real_int = self.convert_bytes_to_int(second_real_byte_array,little_endian=little_endian)

            first_real = float(first_real_int) / 2**32
            second_real = float(second_real_int) / 2**32
            return (first_real,second_real)
        elif data_type == 6:
            return None
        elif data_type == 7:
            return None
        elif data_type == 8:
            return None
        elif data_type == 9:
            return None
        elif data_type == 10:
            return None
        elif data_type == 11:
            return None
        elif data_type == 12:
            return None
        else:
            raise ValueError(f"ERROR[tiff_tag_class.number_of_bytes_for_data_type]: data_type should be between 1-12 instead it was |{data_type}|")

    def get_number_of_bytes_in_data(self):
        number_of_bytes_per_data_type = self.get_number_of_bytes_for_data_type(self.data_type)
        number_of_bytes = self.data_count * number_of_bytes_per_data_type
        return number_of_bytes

    def convert_bytes_to_int(self,input_bytes:bytearray,little_endian=True):
        if little_endian:
            return int.from_bytes(input_bytes,byteorder="little",signed=False)
        else:
            return int.from_bytes(input_bytes,byteorder="big",signed=False)

    def get_number_of_bytes_for_data_type(self,data_type:int):
        if type(data_type) != int:
            raise TypeError(f"ERROR[tiff_tag_class.get_number_of_bytes_for_data_type]: data_type is not of type int instead it is of type |{type(data_type)}|")
        if data_type < 1 or data_type > 12:
            raise ValueError(f"ERROR[tiff_tag_class.number_of_bytes_for_data_type]: data_type should be between 1-12 instead it was |{data_type}|")

        if data_type == 1:
            return 1
        elif data_type == 2:
            return 1
        elif data_type == 3:
            return 2
        elif data_type == 4:
            return 4
        elif data_type == 5:
            return 8
        elif data_type == 6:
            return 1
        elif data_type == 7:
            return 1
        elif data_type == 8:
            return 2
        elif data_type == 9:
            return 8
        elif data_type == 10:
            return 8
        elif data_type == 11:
            return 4
        elif data_type == 12:
            return 8
        else:
            raise ValueError(f"ERROR[tiff_tag_class.number_of_bytes_for_data_type]: data_type should be between 1-12 instead it was |{data_type}|")

    def data_type_in_tag(self,data_type:int):
        if type(data_type) != 'int':
            raise TypeError(f"ERROR[tiff_tag_class.data_type_in_tag]: data_type is not of type bytearray instead it is of type |{type(data_type)}|")
        if data_type < 1 and data_type > 12:
            raise ValueError(f"ERROR[tiff_tag_class.data_type_in_tag]: data_type should be between 1-12 instead it was |{data_type}|")

        if data_type == 1:
            return "BYTE: 8-bit unsigned integer"
        elif data_type == 2:
            return "ASCII: 8-bit, NULL-terminated string"
        elif data_type == 3:
            return "SHORT: 16-bit unsigned integer"
        elif data_type == 4:
            return "LONG: 32-bit unsigned integer"
        elif data_type == 5:
            return "RATIONAL: Two 32-bit unsigned integers"
        elif data_type == 6:
            return "SBYTE: 8-bit signed integer"
        elif data_type == 7:
            return "UNDEFINE: 8-bit byte"
        elif data_type == 8:
            return "SSHORT: 16-bit signed integer"
        elif data_type == 9:
            return "SLONG: 32-bit signed integer"
        elif data_type == 10:
            return "SRATIONAL: Two 32-bit signed integers"
        elif data_type == 11:
            return "FLOAT: 4-byte single-precision IEEE floating-point value"
        elif data_type == 12:
            return "DOUBLE: 8-byte double-precision IEEE floating-point value"
        else:
            raise ValueError(f"ERROR[tiff_tag_class.data_type_in_tag]: data_type should be between 1-12 instead it was |{data_type}|")

class tiff_bitmap_class():
    def __init__(self,data:bytearray):
        self.image_byte_array = data

if __name__ == "__main__":
    temp_string = "C:/Users/Alexander/OneDrive/06 Stereo Camera Set Up/02 Software/03 PNG Meta Data/python-metapng-exif/03 Test Images/small_2.tiff"

    tiff_object = tiff_file_data()
    tiff_object.read_file(temp_string)

    print("finished...")