import ffmpeg
import os

def convert_mp3_to_hls(input_file,output_directory,name,segment_time=10):
    # name = input_file.split(".")[0]
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_m3u8 = os.path.join(output_directory,f"{name}.m3u8")
    output_segment = os.path.join(output_directory,f"{name}_%03d.ts")
    ffmpeg.input(input_file).output(
        output_m3u8,
        format="hls",
        hls_time=segment_time,
        hls_list_size = 0,
        hls_segment_filename = output_segment
        ).run()
    os.remove(input_file)


def main():
    input_file = "fade.mp3"
    output_dir = "hls_output"
    segment_time = 10
    convert_mp3_to_hls(input_file,output_dir,segment_time)

if __name__ == "__main__":
    main()